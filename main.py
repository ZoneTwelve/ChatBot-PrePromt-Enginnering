#!/usr/bin/env python

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import numpy as np
import torch

from os import getenv
from dotenv import dotenv_values

DEFCONF = getenv("CONF", "./config/albert")
BOOTMSG = open(f'{DEFCONF}/welcome', 'r').read()
PPRULES = open(f'{DEFCONF}/rules', 'r').read()
BOTCONF = dotenv_values(f'{DEFCONF}/config')

USER_DELIM  = BOTCONF['USER_DELIM']
RESP_DELIM  = BOTCONF['RESP_DELIM']
END_DELIM   = BOTCONF['END_DELIM']
DELIM_START = BOTCONF['DELIM_START']
DELIM_END   = BOTCONF['DELIM_END']
DENY_DELIM  = BOTCONF['DENY_DELIM']

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_NAME = "ckip-joint/bloom-1b1-zh"

tokenizer = AutoTokenizer.from_pretrained( MODEL_NAME )
model = AutoModelForCausalLM.from_pretrained( MODEL_NAME )

model.to(device)

# Init
print( BOOTMSG )
message = PPRULES

# Test the componment
inputs = tokenizer(message, return_tensors="pt")["input_ids"]
tokens = model.generate(inputs, max_new_tokens=30, do_sample=True)
result = tokenizer.decode(tokens.squeeze())[len(message):]
# Debug
#print('Test:\n---\n', result, '\n---')

while True:
  prompt = input("User: ")
  if(prompt == "print_message"):
    print( message )
    continue
  message += f'\n{USER_DELIM} {prompt}\n{RESP_DELIM} '
  curr_out = ""
  stage = ""
  op = False
  print("AI: ", end="")
  for i in range(64):
    inputs = tokenizer(message, return_tensors="pt")["input_ids"]
    tokens = model.generate(inputs, max_new_tokens=1, do_sample=True)
    start = len(message)
    output = tokenizer.decode(tokens.squeeze(), skip_special_tokens=True)[start:]
    message += output
    stage += output
    
    if DELIM_START == output:
      op = True
    elif DELIM_END == output:
      # do the operation
      curr_out += output
      print(curr_out, DENY_DELIM)
      if END_DELIM == curr_out:
        print("Break")
        break
      if curr_out in DENY_DELIM:
        print("Deny:")
        message.replace( curr_out, "" )
        curr_out = ""
        output = ""
        break
      op = False
    
    if op == True:
      curr_out += output
    else:
      print(output, end="")
    
    if END_DELIM in stage:
      # stage = curr_out.replace( END_DELIM, "" )
      break

  print("")
  # print( "AI:", curr_out.replace("\n", "\n> ").replace(END_DELIM, ""), "\n" )

