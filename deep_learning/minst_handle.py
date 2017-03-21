#! /usr/bin/python
# -*- coding: utf-8 -*-

import struct
from neural_network import Network
from datetime import datetime

# 数据加载器基类
class Loader(object):
    def __init__(self, path, count):
        '''
            初始化加载器
            path: 数据文件路径
            count: 文件中的样本个数
        '''
        self.path = path
        self.count = count

    def get_file_content(self):
        '''读取文件内容'''
        f = open(self.path, 'r')
        content = f.read()
        f.close()
        return content

    def to_int(self, byte):
        '''将unsigned byte字符转换为整数'''
        return struct.unpack('B', byte)[0]


class ImageLoader(Loader):
    def get_picture(self, content, index):
        '''内部函数，从文件中获取图像'''
        start = index * 28 * 28 + 16
        picture = []
        for i in range(28):
            picture.append([])
            for j in range(28):
                picture[i].append( \
                self.to_int(content[start + i * 28 + j]))
        return picture

    def get_one_sample(self, picture):
        '''将图像转换为内部的输入向量'''
        sample = []
        for i in range(28):
            for j in range(28):
                sample.append(picture[i][j])
        print '*** sample ***', sample
        return sample

    def load(self):
        '''加载数据文件，获得全部样本的输入量'''
        conent = self.get_file_content()
        data_set = []
        for index in range(self.count):
            data_set.append( \
                self.get_one_sample(\
                    self.get_picture(conent, index)))
        return data_set

class LabelLoader(Loader):
    def load(self):
        '''加载数据，获取全部的标签向量'''
        content = self.get_file_content()
        labels = []
        for index in range(self.count):
            labels.append(self.norm(content[index + 8]))
        return labels

    def norm(self, label):
        '''内部函数，将一个值转换为10维便签向量'''
        label_vec = []
        label_value = self.to_int(label)
        for i in range(10):
            if i == label_value:
                label_vec.append(0.9)
            else:
                label_vec.append(0.1)
        print '*** label ***', label_vec
        return label_vec

def get_training_data_set():
    '''获得训练数据集'''
    image_loader = ImageLoader('./data/train-images-idx3-ubyte', 60000)
    label_loader = LabelLoader('./data/train-labels-idx1-ubyte', 60000)
    return image_loader.load(), label_loader.load()

def get_test_data_set():
    '''获得测试数据集'''
    image_loader = ImageLoader('./data/t10k-images-idx3-ubyte', 10000)
    label_loader = LabelLoader('./data/t10k-labels-idx1-ubyte', 10000)
    return image_loader.load(), label_loader.load()


def get_result(vec):
    max_value_index = 0
    max_value = 0
    for i in range(len(vec)):
        if vec[i] > max_value:
            max_value = vec[i]
            max_value_index = i
    return max_value_index

def evaluate(network, test_data_set, test_data_labels):
    error = 0
    total = len(test_data_set)
    for i in range(total):
        label = get_result(test_data_labels[i])
        predict = get_result(network.predict(test_data_set[i]))
        if label != predict:
            error += 1
    return float(error) / total

def train_and_evaluate():
    last_error_ratio = 1.0
    epoch = 0
    train_data_set, train_labels = get_training_data_set()
    test_data_set, test_labels = get_test_data_set()
    network = Network([784, 300, 10])
    while True:
        epoch += 1
        network.train(train_labels, train_data_set, 0.3, 1)
        print '%s epoch %d finished' % (now(), epoch)
        if epoch % 10 == 0:
            epoch_error = evaluate(network, test_data_set, test_labels)
            print '%s after epoch %d, error ratio is %f' % (now(), epoch, error_ratio)
            if epoch_error > last_error_ratio:
                break
            else:
                last_error_ratio = epoch_error

if __name__ == '__main__':
    train_and_evaluate()


