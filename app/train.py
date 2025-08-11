import os
import pandas as pd
import torch
import random
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    MT5ForConditionalGeneration,
    MT5Tokenizer,
    Trainer,
    TrainingArguments,
)

os.environ["WANDB_DISABLED"] = "true"

device = torch.device("cuda")

df = pd.read_csv("dataset.csv")

latin_to_cyrillic_map = str.maketrans({
    "o": "о", "a": "а", "e": "е", "c": "с", "x": "х", "y": "у",
    "O": "О", "A": "А", "E": "Е", "C": "С", "X": "Х", "Y": "У"
})

def normalize_text(text):
    return text.translate(latin_to_cyrillic_map)

synonym_replacements = {
    "создадена": "создадено",
    "добар": "добра",
    "еден": "една",
}

extra_errors = [
    (" и ", " "),  
    (",", ""),     
    (" во ", " на "), 
]

def introduce_errors(sentence):
    words = sentence.split()
    for i, w in enumerate(words):
        if w in synonym_replacements and random.random() < 0.7:
            words[i] = synonym_replacements[w]
    noisy_sentence = " ".join(words)
    for src, tgt in extra_errors:
        if random.random() < 0.5:
            noisy_sentence = noisy_sentence.replace(src, tgt)
    return noisy_sentence

synthetic_data = []
for _, row in df.iterrows():
    correct = normalize_text(row["modified_sentence"])
    incorrect = normalize_text(row["original_sentence"])
    synthetic_incorrect = introduce_errors(correct)
    synthetic_data.append((incorrect, correct))
    synthetic_data.append((synthetic_incorrect, correct))

synthetic_data = synthetic_data * 3

aug_df = pd.DataFrame(synthetic_data, columns=["input_sentence", "target_sentence"])
aug_df = aug_df.drop_duplicates()
aug_df["input_text"] = "исправи реченица: " + aug_df["input_sentence"]
aug_df["target_text"] = aug_df["target_sentence"]

dataset = Dataset.from_pandas(aug_df[["input_text", "target_text"]])

model_name = "google/mt5-small"
tokenizer = MT5Tokenizer.from_pretrained(model_name)
model = MT5ForConditionalGeneration.from_pretrained(model_name).to(device)

def tokenize(examples):
    model_inputs = tokenizer(
        examples["input_text"],
        truncation=True,
        padding="max_length",
        max_length=128,
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            examples["target_text"],
            truncation=True,
            padding="max_length",
            max_length=128,
        )
    labels["input_ids"] = [[tid if tid != tokenizer.pad_token_id else -100 for tid in ids] for ids in labels["input_ids"]]
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["input_text", "target_text"])

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

training_args = TrainingArguments(
    output_dir="./mt5-mk-corrector",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=15,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    logging_steps=50,
    save_steps=500,
    save_total_limit=2,
    fp16=False,
    logging_dir="./logs",
    report_to=None,
)

tokenized_dataset = tokenized_dataset.shuffle(seed=42)
split = tokenized_dataset.train_test_split(test_size=0.1)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=split["train"],
    eval_dataset=split["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

model.save_pretrained("./mt5-mk-corrector")
tokenizer.save_pretrained("./mt5-mk-corrector")

def correct_sentence(sentence):
    inputs = tokenizer("исправи реченица: " + sentence, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=64, num_beams=8, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)