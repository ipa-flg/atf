#!/usr/bin/env python
import numpy
import rospy
from copy import deepcopy
from atf_msgs.msg import *
import time


class CalculateResources:
    """
    Class for calculating the average resource workload and writing the current resource data.
    The resource data is sent over the topic "/testing/Resources".
    """
    def __init__(self, resources):
        """
        Constructor.

        @param resources: a list of dictionaries containing the names of the resources and a list with
        the names of the nodes. Example: {"cpu":[move_group]}
        @type  resources: dict
        """

        self.active = False
        self.resources = resources
        self.node_data = {}
        self.size_io = len(IO.__slots__)
        self.size_network = len(Network.__slots__)
        self.average_data = {}
        self.activation_time = rospy.Time()

        # Sort resources after nodes
        for resource in self.resources:
            for node in self.resources[resource]:
                if node not in self.node_data:
                    self.node_data[node] = {resource: []}
                elif resource not in self.node_data[node]:
                    self.node_data[node].update({resource: []})

        self.average_data = deepcopy(self.node_data)

        rospy.Subscriber("/testing/Resources", Resources, self.process_resource_data, queue_size=1)

    def start(self):
        self.active = True
        self.activation_time = rospy.Time(time.time())

    def stop(self):
        self.active = False

    def process_resource_data(self, msg):
        if self.active:
            for node in msg.nodes:
                try:
                    for resource in self.node_data[node.node_name]:
                        if resource == "cpu":
                            self.node_data[node.node_name][resource].append(round(node.cpu, 2))
                        elif resource == "mem":
                            self.node_data[node.node_name][resource].append(round(node.memory, 2))
                        elif resource == "io":
                            if len(self.node_data[node.node_name][resource]) == 0:
                                for i in xrange(0, self.size_io):
                                    self.node_data[node.node_name][resource].append([])
                            self.node_data[node.node_name][resource][0].append(round(node.io.read_count, 2))
                            self.node_data[node.node_name][resource][1].append(round(node.io.write_count, 2))
                            self.node_data[node.node_name][resource][2].append(round(node.io.read_bytes, 2))
                            self.node_data[node.node_name][resource][3].append(round(node.io.write_bytes, 2))
                        elif resource == "network":
                            if len(self.node_data[node.node_name][resource]) == 0:
                                for i in xrange(0, self.size_network):
                                    self.node_data[node.node_name][resource].append([])
                            self.node_data[node.node_name][resource][0].append(round(node.network.bytes_sent, 2))
                            self.node_data[node.node_name][resource][1].append(round(node.network.bytes_recv, 2))
                            self.node_data[node.node_name][resource][2].append(round(node.network.packets_sent, 2))
                            self.node_data[node.node_name][resource][3].append(round(node.network.packets_recv, 2))
                            self.node_data[node.node_name][resource][4].append(round(node.network.errin, 2))
                            self.node_data[node.node_name][resource][5].append(round(node.network.errout, 2))
                            self.node_data[node.node_name][resource][6].append(round(node.network.dropin, 2))
                            self.node_data[node.node_name][resource][7].append(round(node.network.dropout, 2))
                except KeyError:
                    pass

    def get_result(self):

        for node in self.node_data:
            for res in self.node_data[node]:
                if res == "io" or res == "network":
                    for values in self.node_data[node][res]:
                        self.average_data[node][res].append(float(round(numpy.mean(values), 2)))
                else:
                    self.average_data[node][res] = float(round(numpy.mean(self.node_data[node][res]), 2))

        # print self.average_data
        # return ""
        return self.activation_time.to_sec(), ["resources", "average_resources"], [self.node_data, self.average_data]
