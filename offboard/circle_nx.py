import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import *
from mavros_msgs.srv import *
from tf.transformations import euler_from_quaternion
import threading
from nav_msgs.msg import Odometry
import numpy as np
import math

def thread_job():
    rospy.spin()

def angel2rad(angel):
    return angel/180*math.pi

class Controller:
    
    def __init__(self):

       
        self.state = State()
       
        self.local_pos = PoseStamped()
        self.vins_pos = Odometry()
        self.ifcircle = False
        self.target_sp = PoseStamped()
        self.target_sp.pose.position.x = 0
        self.target_sp.pose.position.y = 0
        self.target_sp.pose.position.z = 0.5
        
        self.cur_pos = PoseStamped()
        self.thred = 0.1

        self.start_time = rospy.Time.now()
        self.cur_time = rospy.Time.now()
        self.t = 2
        
       

    def posCb(self, msg):
        self.vins_pos = msg
        self.local_pos.pose.position.x = msg.pose.pose.position.x
        self.local_pos.pose.position.y = msg.pose.pose.position.y
        self.local_pos.pose.position.z = msg.pose.pose.position.z
        self.local_pos.pose.orientation.x = msg.pose.pose.orientation.x
        self.local_pos.pose.orientation.y = msg.pose.pose.orientation.y
        self.local_pos.pose.orientation.z = msg.pose.pose.orientation.z
        self.local_pos.pose.orientation.w = msg.pose.pose.orientation.w
        self.local_pos.header.stamp = rospy.Time.now()
        vision_pub = rospy.Publisher("/mavros/vision_pose/pose",PoseStamped, queue_size = 1)
        vision_pub.publish(self.local_pos)

    def stateCb(self, msg):
        self.state = msg
        print("current mode is: ",self.state.mode)

    def refCb(self, msg):
        self.cur_pos = msg
        quaternion = [msg.pose.orientation.x,msg.pose.orientation.y,msg.pose.orientation.z,msg.pose.orientation.w]
        euler = euler_from_quaternion(quaternion)
        # print("current_pos: " , self.cur_pos.pose.position.x,self.cur_pos.pose.position.y,self.cur_pos.pose.position.z)
        # print("current_pose: ", euler)

    def distance(self):
        diff = np.array([self.target_sp.pose.position.x - self.cur_pos.pose.position.x, 
            self.target_sp.pose.position.y - self.cur_pos.pose.position.y,
            self.target_sp.pose.position.z - self.cur_pos.pose.position.z])
        dis = np.linalg.norm(diff)
        return dis

    def settarget(self):
        #self.cur_time = event.current_real
        self.cur_time = rospy.Time.now()
        dett = (self.cur_time.to_sec() - self.start_time.to_sec())
        # rospy.loginfo("dett:{}".format(dett))
        # print("dett:",dett/1e8)
        self.target_sp.pose.position.y = 0.5*math.sin(angel2rad(360/self.t*dett))
        self.target_sp.pose.position.x = 0.5-0.5*math.cos(angel2rad(360/self.t*dett))
        self.target_sp.pose.position.z = 0.5


def main():
    print("start!")
    rospy.init_node('offboard_test_node', anonymous=True)
    cnt = Controller()
    rate = rospy.Rate(200)
    rospy.Subscriber('/mavros/state', State, cnt.stateCb)
    rospy.Subscriber("/vins_estimator/odometry", Odometry, cnt.posCb)
    rospy.Subscriber("/mavros/local_position/pose", PoseStamped,cnt.refCb)

    add_thread = threading.Thread(target = thread_job)
    add_thread.start()

    sp_pub = rospy.Publisher("mavros/setpoint_position/local", PoseStamped, queue_size = 1)

    # ROS main loop
    while not rospy.is_shutdown():
        #print("distance:",cnt.distance())
        print("ifcircle:",cnt.ifcircle)
        if (cnt.distance() < cnt.thred) and (not cnt.ifcircle):
            cnt.ifcircle = True
            cnt.start_time = rospy.Time.now()
            print("enter circle!")            
        if cnt.ifcircle:
            cnt.settarget()

        cnt.target_sp.header.stamp = rospy.Time.now()
        sp_pub.publish(cnt.target_sp) 
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
