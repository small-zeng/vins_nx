#!/usr/bin/env python
import rospy
from geometry_msgs.msg import *
from mavros_msgs.msg import *
from mavros_msgs.srv import *
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
import time


class Logger:
    def __init__(self):
        self.f = open("/home/nvidia/vins_ws/path/record.txt", 'w')
        self.vins_pose = [str(0),str(0),str(0),str(0),str(0),str(0)]
        self.opti_pose = [str(0),str(0),str(0),str(0),str(0),str(0)]
        self.extri = [str(0),str(0),str(0),str(0),str(0),str(0)]
        test = Odometry()
        test.pose.pose.orientation.x
        
        self.start_time = 0 
        self.cur_time = 0
        rospy.Subscriber("/vins_estimator/odometry", Odometry,self.vins_Cb)
        rospy.Subscriber("/vrpn_client_node/liudandi/pose",PoseStamped,self.opti_Cb)
        rospy.Subscriber("/vins_estimator/extrinsic", Odometry,self.extri_Cb)
        

    def write_data(self):
        self.cur_time = time.clock()
        self.f.write(str(self.cur_time-self.start_time))
        self.f.write(',')
        self.f.write(','.join(self.vins_pose))
        self.f.write(',')
        self.f.write(','.join(self.opti_pose))
        self.f.write(',')
        self.f.write(','.join(self.extri))
        self.f.write('\r\n')
        
    def write_title(self):
        self.f.write("time, vins_x, vins_y, vins_z, vins_roll, vins_pitch, vins_yaw,opti_x, opti_y, opti_z, opti_roll, opti_pitch, opti_yaw, extri_x, extri_y, extri_z, extri_roll, extri_pitch, extri_yaw")
        self.f.write('\r\n')

    def opti_Cb(self,msg):
        quaternion = [msg.pose.orientation.x,msg.pose.orientation.y,msg.pose.orientation.z,msg.pose.orientation.w]
        euler = euler_from_quaternion(quaternion)
        self.opti_pose = [str(msg.pose.position.x), str(msg.pose.position.y), str(msg.pose.position.z), str(euler[0]),str(euler[1]),str(euler[2])]
    
    def vins_Cb(self,msg):
        quaternion = [msg.pose.pose.orientation.x,msg.pose.pose.orientation.y,msg.pose.pose.orientation.z,msg.pose.pose.orientation.w]
        euler = euler_from_quaternion(quaternion)
        self.vins_pose = [str(msg.pose.pose.position.x), str(msg.pose.pose.position.y), str(msg.pose.pose.position.z), str(euler[0]),str(euler[1]),str(euler[2])]
    
    def extri_Cb(self,msg):
        quaternion = [msg.pose.pose.orientation.x,msg.pose.pose.orientation.y,msg.pose.pose.orientation.z,msg.pose.pose.orientation.w]
        euler = euler_from_quaternion(quaternion)
        self.extri = [str(msg.pose.pose.position.x), str(msg.pose.pose.position.y), str(msg.pose.pose.position.z), str(euler[0]),str(euler[1]),str(euler[2])]

def main():
    print("start record!")
    rospy.init_node('record_node', anonymous=True)
    logger = Logger()
    rate = rospy.Rate(200)
    logger.start_time = time.clock()
    logger.write_title()
    while not rospy.is_shutdown():
        logger.write_data()
        rate.sleep()
    logger.f.close()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
