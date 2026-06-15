import rclpy
from rclpy.node import Node
import sys

def main():
    rclpy.init()
    node = Node('temp_test_node')
    print("Node names:", node.get_node_names())
    print("Node names and namespaces:", node.get_node_names_and_namespaces())
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
