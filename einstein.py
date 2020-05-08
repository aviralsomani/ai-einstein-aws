import gpt_2_simple as gpt2
import os

seed = "hello"
sess = gpt2.start_tf_sess()

gpt2.load_gpt2(sess)
text = gpt2.generate(sess,
              length=500,
              prefix=seed,
              return_as_list=True)[0]

print(text)




