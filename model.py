import gpt_2_simple as gpt2


class EinsteinModel:
    def __init__(self):
        self.sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.sess)

    def generate(self, prompt='Hello', length=500):
        text = gpt2.generate(self.sess, length=length, prefix=prompt, return_as_list=True)[0]
        text = text.replace('\\\'e2\\\'80\\\'99', '\'')
        text = text.replace('<|endoftext|>', '')
        text = text.split('<|startoftext|>')
        return text

