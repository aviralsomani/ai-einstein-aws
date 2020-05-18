import os
os.system("source activate tensorflow_p36")

import gpt_2_simple as gpt2

class EinsteinModel:
    def __init__(self):
        self.sess = gpt2.start_tf_sess()
        self.checkpoint_dir = str("/home/ubuntu/git/ai-einstein-aws/checkpoint")
        gpt2.load_gpt2(self.sess, checkpoint_dir=self.checkpoint_dir)

    def generate(self, prompt='Hello', length=500):
        text = gpt2.generate(self.sess, length=length, checkpoint_dir=self.checkpoint_dir, prefix=prompt, return_as_list=True)[0]
        text = text.replace('\\\'e2\\\'80\\\'99', '\'')
        text = text.replace('<|endoftext|>', '')
        text = text.split('<|startoftext|>')
        return text

