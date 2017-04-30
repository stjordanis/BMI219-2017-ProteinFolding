import chainer
from chainer import functions as F
from chainer import links as L

from lib.models import mlp
from lib.models import cnn as cnn_
from lib.models import rnn as rnn_


class Model(chainer.Chain):

    @property
    def train(self):
        return self._train

    @train.setter
    def train(self, val):
        for l in self.children():
            l.train = val
        self._train = val

    def __call__(self, x):
        timestep = x.data.shape[1]
        is_seq = acid.data != -1
        x = self.embed(x)
        x = F.expand_dims(x, 1)
        x = F.relu(self.cnn(x))
        xs = F.split_axis(x, timestep, 2)
        xs = self.rnn(xs, is_seq)
        ys = [self.fc(x) for x in xs]
        return F.stack(ys, -1)


def make_model(vocab, embed_dim, channel_num,
               rnn_dim, fc_dim, class_num):
    embed = L.EmbedID(vocab, embed_dim, ignore_label=-1)

    channels = (channel_num,) * 3
    windows = [(3, embed_dim), (7, embed_dim), (11, embed_dim)]
    cnn = cnn_.MultiScaleCNN(1, channels, windows)

    conv_out_dim = channel_num * 3
    rnn = rnn_.StackedBiRNN(conv_out_dim, rnn_dim)

    fc = mlp.MLP(fc_dim, class_num)

    model = Model(embed=embed, cnn=cnn, rnn=rnn, fc=fc)
    model.train = True
    return model
