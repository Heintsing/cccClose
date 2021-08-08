# !/usr/bin/env python
# -*- coding:UTF-8 -*-

import numpy as np
import pandas as pd
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Run on CPU
import scipy.io as sio
import tensorflow as tf
import argparse
import os

Result_path = r'E:\action0726\class\result1'


class SMnistModel:

    def __init__(self,  model_size, learning_rate=0.0001):
        self.constrain_op = None
        self.x = tf.placeholder(dtype=tf.float32, shape=[200, 1, 64])

        self.model_size = model_size
        head = self.x
        # head = tf.expand_dims(head, axis=1)


        self.fused_cell = tf.nn.rnn_cell.LSTMCell(model_size)

        head, _ = tf.nn.dynamic_rnn(self.fused_cell, head, dtype=tf.float32, time_major=True)


        print("head.shape: ", str(head.shape))
        # if (model_type.startswith("ltc")):
        #     print("state.shape: ", str(state.shape))
        unstack_head = tf.unstack(head, axis=0)  # 拆成64个张量的list 每一个大小为batch_size*inputs
        # print("unstack_head.shape: ", str(unstack_head))

        head = unstack_head[-1]
        print("head.shape: ", str(head.shape))
        head1 = tf.layers.Dense(32, activation=None)(head)
        self.y = tf.layers.Dense(6, activation=None)(head1)

        # self.y = tf.layers.Dense(33, activation=None)(head)
        print("logit shape: ", str(self.y.shape))
        # self.loss = tf.reduce_mean(tf.losses.sparse_softmax_cross_entropy(
        #     labels=self.target_y,
        #     logits=self.y,
        # ))

        # optimizer = tf.train.AdamOptimizer(learning_rate)
        # self.train_step = optimizer.minimize(self.loss)

        self.model_prediction = tf.argmax(input=self.y, axis=1)

        self.sess = tf.InteractiveSession()
        self.sess.run(tf.global_variables_initializer())

        self.checkpoint_path = os.path.join(Result_path, "tf_sessions", "{}_{}".format('lstm', model_size))
        if (not os.path.exists(self.checkpoint_path)):
            os.makedirs(self.checkpoint_path)

        self.saver = tf.train.Saver()

    # def save(self):
    #     self.saver.save(self.sess, self.checkpoint_path)

    def restore(self):
        self.saver.restore(self.sess, self.checkpoint_path)

    def test(self, input, verbose=True):
        # ax = []
        # ay_test_loss = []
        prediction = []
        self.restore()

        if verbose:
            model_prediction = self.sess.run([self.model_prediction],
                                                                  {self.x: input,
                                                                   })
            model_prediction = np.array(model_prediction)
            model_prediction = np.squeeze(model_prediction)
            # print(model_prediction.shape)
            # print(model_prediction.dtype)
            print(
                "model_prediction: "+
                    str(model_prediction)
                )
            # prediction.extend(model_prediction)
        return model_prediction


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', default=32, type=int)
    args = parser.parse_args()

    # occ_data = SMnistData()
    model = SMnistModel(model_size=args.size)
    occ_data = np.array(pd.read_csv(r'E:\action0726\class\result1\test_x.csv', header=None))[:200, :]
    occ_data = np.expand_dims(occ_data, axis=1)
    re = model.test(occ_data)
