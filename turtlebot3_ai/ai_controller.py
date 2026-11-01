import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

import numpy as np
import math


class TurtleBotAI(Node):

    def __init__(self):
        super().__init__('turtlebot_ai')

        # LiDARを受信
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # 移動命令を送信
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info('TurtleBot AI started!')

    def scan_callback(self, msg):

        ranges = np.array(msg.ranges)

        # 無限大やNaNを処理
        ranges = np.nan_to_num(
            ranges,
            nan=3.5,
            posinf=3.5
        )

        n = len(ranges)

        # ===== AIへの入力データ =====

        # 前方
        front = min(
            np.min(ranges[0:n // 12]),
            np.min(ranges[-n // 12:])
        )

        # 左側
        left = np.min(ranges[n // 6:n // 3])

        # 右側
        right = np.min(ranges[2 * n // 3:5 * n // 6])

        # ===== 独自AIの判断 =====

        action = self.ai_decision(front, left, right)

        # ===== 行動を決定 =====

        cmd = Twist()

        if action == "FORWARD":
            cmd.linear.x = 0.15

        elif action == "LEFT":
            cmd.angular.z = 0.7

        elif action == "RIGHT":
            cmd.angular.z = -0.7

        # TurtleBot3へ送信
        self.cmd_pub.publish(cmd)

    def ai_decision(self, front, left, right):

        # ここが「独自AI」の部分です

        safe_distance = 0.6

        # 前方が安全なら前進
        if front > safe_distance:
            return "FORWARD"

        # 左右の広い方を選択
        if left > right:
            return "LEFT"
        else:
            return "RIGHT"


def main(args=None):

    rclpy.init(args=args)

    node = TurtleBotAI()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
