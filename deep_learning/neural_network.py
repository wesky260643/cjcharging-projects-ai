#! /usr/bin/python
# -*- coding: utf-8 -*-

import random

class Node(object):
    def __init__(self, layer_index, node_index):
        '''
            构造节点对象
            layer_index: 节点所属的层编号
            node_index：节点的编号
        '''
        self.layer_index = layer_index
        self.node_index = node_index
        self.downstream = []
        self.upstream = []
        self.output = 0
        self.delta = 0

    def set_output(self, output):
        '''设置节点的输出值，如果节点属于输入层，会用到这个函数A'''
        self.output = output

    def append_downstream_connection(self, conn):
        '''添加一个到下游节点的连接'''
        self.downstream.append(conn)

    def append_upstream_connection(self, conn):
        '''添加一个到上游节点的连接'''
        self.upstream.append(conn)

    def calc_output(self):
        '''计算节点的输出：上游节点的输出*权重，再运用激活函数'''
        output = reduce(lambda ret, conn: conn.upstream_node.output * conn.weight, \
                self.upstream, 0.0)
        self.output = sigmoid(output)

    def calc_hidden_layer_delta(self):
        '''计算隐藏层节点的误差项：下游反向误差*激活函数的导数'''
        downstream_delta = reduce(lambda ret, conn: ret + conn.downstream_node.delta * conn.weight, \
                self.downstream, 0.0)
        self.delta = self.output * (1 - self.output) * downstream_delta

    def calc_output_layer_delta(self, label):
        '''计算输出层误差项'''
        self.delta = self.output * (1 - self.output) * (label - self.output)

    def __str__(self):
	'''打印节点的信息'''
        node_str = '%u-%u: output: %f delta: %f' % \
		(self.layer_index, self.node_index, self.output, self.delta)
	downstream_str = reduce(lambda ret, conn: ret + '\n\t' + str(conn), self.downstream, '')
        upstream_str = reduce(lambda ret, conn: ret + '\n\t' + str(conn), self.upstream, '')
        return node_str + '\n\tdownstream:' + downstream_str + '\n\tupstream:' + upstream_str

class ConstNode(object):
    '''实现输出恒为1的节点'''
    def __init__(self, layer_index, node_index):
	'''
            构造节点对象。
            layer_index: 节点所属的层的编号
            node_index: 节点的编号
        '''
        self.layer_index = layer_index
        self.node_index = node_index
        self.downstream = []
        self.output = 1

    def append_downstream_connection(self, conn):
        '''添加一个到下游节点的连接'''
        self.downstream.append(conn)

    def calc_hidden_layer_delta(self):
        '''计算隐藏层节点的误差'''
        downstream_delta = reduce(lambda ret, conn: ret + \
                conn.downstream_node.delta * conn.weight, self.downstream, 0.0)
        self.delta = self.output * (1 - self.output) * downstream_delta


class Layer(object):
    '''Layer对象，负责初始化一层，此外，作为node集合对象提供对node集合的操作'''
    def __init__(self, layer_index, node_count):
        '''
            初始化一层
            layer_index: 层编号
            node_count：层所包含的节点数
        '''
        self.layer_index = layer_index
        self.nodes = []
        for i in range(node_count):
            self.nodes.append(Node(layer_index, i))
        self.nodes.append(ConstNode(layer_index, node_count))

    def set_output(self, data):
        '''设置层的输出，当层是输入层时会用到'''
        for i in range(len(data)):
            self.nodes[i].set_output(data[i])

    def calc_output(self):
        '''计算层的输出'''
        for i in self.nodes[:-1]:
            self.nodes[i].calc_output()

    def dump(self):
        '''打印层的信息'''
        for node in self.nodes:
            print node


class Connection(object):
    '''记录连接的权重，以及上下游所关注的点'''
    def __init__(self, upstream_node, downstream_node):
        '''
            初始化连接，权重初始化为一个很小的随机数
            upstream_node：连接的上游节点
            downstream_node:连接的下游节点
        '''
        self.upstream_node = upstream_node
        self.downstream_node = downstream_node
        self.weight = random.uniform(-0.1, 0.1)
        self.gradient = 0.0

    def calc_gradient(self):
        '''计算梯度：下游节点的反向传导误差*上游节点的输出'''
        self.gradient = self.upstream_node.output * self.downstream_node.delta

    def get_gradient(self):
        '''获取梯度'''
        return self.gradient

    def update_weight(self, rate):
        self.calc_gradient()
        self.weight += rate * self.gradient

    def __str__(self):
	'''
        打印连接信息
        '''
        return '(%u-%u) -> (%u-%u) = %f' % (
            self.upstream_node.layer_index,
            self.upstream_node.node_index,
            self.downstream_node.layer_index,
            self.downstream_node.node_index,
            self.weight)


class Connections(object):
    '''提供connection集合的操作'''
    def __init__(self):
	self.connections = []

    def add_connection(self, connection):
        self.connections.append(connection)

    def dump(self):
        for conn in self.connections:
            print conn

class Network(object):
    def __init__(self, layers):
        '''
        初始化一个全连接神经网络
        layers: 数组，描述神经网络每层节点数
        '''
        self.connections = Connections()
        self.layers = []
        layer_count = len(layers)
        node_count = 0
        for i in range(layer_count):
            self.layers.append(Layer(i, layers[i]))
        for layer in range(layer_count - 1):
            connections = [Connection(upstream_node, downstream_node) \
                        for upstream_node in self.layers[layer].nodes \
                        for downstream_node in self.layers[layer+1].nodes[:-1]]
            for conn in connections:
                self.connections.add_connection(conn)
                conn.downstream_node.append_upstream_connection(conn)
                conn.upstream_node.append_downstream_connection(conn)

    def train(self, labels, data_set, rate, iteration):
        '''
            训练神经网络
            labels:数组，训练样本的标签，每个元素是一个样本的标签
            date_set:二维数据，训练样本特征，每个元素是一个样本的特征
        '''
        for i in range(iteration):
            for d in range(len(data_set)):
                self.train_one_sample(labels[d], data_set[d], rate)

    def train_one_sample(self, label, sample, rate):
        '''内部函数，用一个样本训练网络'''
        self.predict(sample)
        self.calc_delta(label)
        self.update_weight(rate)

    def calc_delta(self, label):
        '''内部函数，计算每个节点的delta'''
        output_nodes = self.layers[-1].nodes
        for i in range(len(label)):
            output_nodes[i].calc_output_layer_delta(label[i])
        for layer in self.layers[-2::-1]:
            for node in layer.nodes:
                node.calc_hidden_layer_delta()

    def update_weight(self, rate):
        '''内部函数，更新每个连接的权重'''
        for layer in self.layers[:-1]:
            for node in layer.nodes:
                for conn in node.downstream:
                    conn.update_weight(rate)

    def calc_gradient(self):
        '''内部函数，计算每个连接的梯度'''
        for layer in self.layers[:-1]:
            for node in layer.nodes:
                for conn in node.downstream:
                    conn.calc_gradient()

    def get_gradient(self, label, sample):
        '''获得网络在一个样本下，每个连接上的梯度
            label: 样本标签
            sample：样本输入
        '''
        self.predict(sample)
        self.calc_delta(label)
        self.calc_gradient()

    def predict(self, sample):
        '''
        根据输入的样本预测输出值
        sample: 数组，样本的特征，也就是网络的输入向量
        '''
	self.layers[0].set_output(sample)
	for i in range(1, len(self.layers)):
            self.layers[i].calc_output
	return map(lambda node: node.output, self.layers[-1].nodes[:-1])

    def dump(self):
        '''打印网络信息'''
        for layer in self.layers:
            print layer
