'''
Created on 07.02.2014

@author: tatsch
'''
import sys
import math
import numpy as np  # for cross, inv, random, arange
from navdata import Navdata

if(sys.platform != "skulpt"):
    import matplotlib.pyplot as plt
    from pylab import *
    from mpl_toolkits.mplot3d import Axes3D
    import time

class Simulator():
    
    start_time = 0  # in secs
    end_time = 10
    dt = 0.05

    
    def __init__(self, drone, controller):
        self.drone = drone
        self.controller = controller
        
        if(sys.platform != "skulpt"):
            self.x = []
            self.y = []
            self.z = []
            self.roll = []
            self.pitch = []
            self.yaw = []
            self.cmd1 =[]
            self.cmd2 =[]
            self.cmd3 =[]
            self.cmd4 =[]
            self.e_yaw=[]
            self.e_x=[]
            self.e_y=[]
            self.e_z=[]
            self.roll_des=[]
            self.pitch_des=[]
            self.yaw_des=[]

    
    def reset(self):
        # TODO: reset all states
        self.theta_desired = np.array([[0.2], [0.0], [0.0]])
        self.thetadot_desired = np.array([[0.0], [0.0], [0.0]])
        self.x_desired = np.array([[0.0], [0.0], [0.0]])
        self.xdot_desired = np.array([[0.0], [0.0], [0.0]])
        self.drone.x = np.array([[0.0],[0.0],[0.0]])
        self.drone.xdot = np.array([[0.0],[0.0],[0.0]])
        self.drone.xdoubledot = np.array([[0.0],[0.0],[0.0]])
    
    def get_drone_pose(self):
        return [self.drone.x.item(0), self.drone.x.item(1), self.drone.x.item(2), self.drone.theta.item(0), self.drone.theta.item(1), self.drone.theta.item(2)];
    
    def get_drone_navdata(self):
        navdata=Navdata(self)
        navdata.vx=self.drone.xdot.item(0)
        navdata.vy=self.drone.xdot.item(1)
        navdata.vz=self.drone.xdot.item(2)
        navdata.ax=self.drone.xdoubledot(0)
        navdata.ay=self.drone.xdoubledot(1)
        navdata.az=self.drone.xdoubledot(2)
        navdata.altd=self.drone.x.item(2)
        navdata.rotX=self.drone.theta.item(0)
        navdata.rotX=self.drone.theta.item(1)
        navdata.rotX=self.drone.theta.item(2)
        return navdata;
    
    def simulate_step(self, t, dt):

        inputCurrents,e_x,e_y,e_z,e_yaw,roll_des,pitch_des,yaw_des = self.controller.calculate_control_command(self.theta_desired, self.thetadot_desired,self.x_desired,self.xdot_desired)
        omega = self.thetadot2omega(self.drone.thetadot, self.drone.theta)  # calculate current angular velocity
        linear_acceleration = self.linear_acceleration(inputCurrents, self.drone.theta, self.drone.xdot)  # calculate the resulting linear acceleration
        omegadot = self.angular_acceleration(inputCurrents, omega)  # calculate resulting angular acceleration
        omega = omega + self.dt * omegadot  # integrate up new angular velocity in the body frame
        self.drone.thetadot = self.omega2thetadot(omega, self.drone.theta)  # calculate roll, pitch, yaw velocities
        self.drone.theta = self.drone.theta + self.dt * self.drone.thetadot  # calculate new roll, pitch, yaw angles
        #print("New theta",self.drone.theta)
        self.drone.xdoubledot=linear_acceleration
        self.drone.xdot = self.drone.xdot + self.dt * linear_acceleration  # calculate new linear drone speed
        self.drone.x = self.drone.x + self.dt * self.drone.xdot  # calculate new drone position
        print "acc", linear_acceleration
        print "theta", self.drone.theta
        #print("Position",self.drone.x.transpose())
        
        if(sys.platform != "skulpt"):#save trajectory for plotting
            self.x.append(self.drone.x.item(0))
            self.y.append(self.drone.x.item(1))
            self.z.append(self.drone.x.item(2))
            self.roll.append(self.drone.theta.item(0))
            self.pitch.append(self.drone.theta.item(1))
            self.yaw.append(self.drone.theta.item(2))
            print self.theta_desired.item(2)
            self.cmd1.append(inputCurrents[0])
            self.cmd2.append(inputCurrents[1])
            self.cmd3.append(inputCurrents[2])
            self.cmd4.append(inputCurrents[3])
            self.e_yaw.append(e_yaw)
            self.e_x.append(e_x)
            self.e_y.append(e_y)
            self.e_z.append(e_z)
            self.roll_des.append(roll_des)
            self.pitch_des.append(pitch_des)
            self.yaw_des.append(yaw_des)


    
    def simulate(self, duration):
        self.end_time = duration
        self.reset();
        # Step through the simulation, updating the drone state.
        t=self.start_time
        fig1=figure(1)
        fig2=figure(2)                
        fig3=figure(3)                
        fig4=figure(4)                


        while t <= self.end_time:
            self.simulate_step(t, self.dt)
            t += self.dt
        
            if(sys.platform != "skulpt"):
                #ion()
                ###########################################
                plt.figure(1)
                fig1.suptitle('Position x,y,z')
                #ax=fig1.add_subplot(111, projection='3d')
                #ax.plot(self.x, self.y, self.z)
                #ax.axis([-5, 5, -5, 5])
                #ax.set_zlim3d( -5, 5 )
                #ax.set_xlabel('x')
                #ax.set_ylabel('y')
                #ax.set_zlabel('z')
                plt.ylim(-1.5,+1.5)
                plt.xlim(-1.5,+1.5)               
                ax=fig1.add_subplot(111)
                ax.plot(self.x, self.y)
                draw()
                fig1.show()

                ###########################################
                plt.figure(2)
                fig2.suptitle('Position roll, pitch, yaw')
                ax_roll=fig2.add_subplot(311)
                ax_roll.plot(self.roll)
                ax_roll.plot(self.roll_des)
                #ax_roll.legend("des","act",right)
                ax_pitch=fig2.add_subplot(312, sharey=ax_roll)
                ax_pitch.plot(self.pitch)
                ax_pitch.plot(self.pitch_des)

                ax_yaw=fig2.add_subplot(313, sharey=ax_roll)
                ax_yaw.plot(self.yaw)
                ax_yaw.plot(self.yaw_des)
                draw()
                fig2.show()
 
                ###########################################
                plt.figure(3)
                plt.ylim(-5,+5)               
                fig3.suptitle('Errors x,y,z,yaw ')
                ax_x=fig3.add_subplot(411)
                ax_x.plot(self.e_x)
                ax_y=fig3.add_subplot(412, sharey=ax_x)
                ax_y.plot(self.e_y)
                ax_z=fig3.add_subplot(413, sharey=ax_x)
                ax_z.plot(self.e_z)
                ax_yaw=fig3.add_subplot(414, sharey=ax_x)
                ax_yaw.plot(self.e_yaw)
                draw()
                fig3.show()
                ###########################################
                plt.figure(4)
                plt.ylim(-2,2)               
                fig4.suptitle('Control Commands')
                ax_1=fig4.add_subplot(411)
                ax_1.plot(self.cmd1)
                ax_2=fig4.add_subplot(412,sharey=ax_1)
                ax_2.plot(self.cmd2)
                ax_3=fig4.add_subplot(413,sharey=ax_1)
                ax_3.plot(self.cmd3)
                ax_4=fig4.add_subplot(414,sharey=ax_1)
                ax_4.plot(self.cmd4)
                fig4.show()
                pause(1)
        
    def deg2rad(self,degrees):
        return np.array(map(math.radians, degrees))
        
    def rotation(self, angles):  # translate angles to intertial/world frame
        phi = angles.item(0)
        theta = angles.item(1)
        psi = angles.item(0)
        #ZYZ Euler nach Paper
        R = np.array([[math.cos(phi) * math.cos(psi) - math.cos(theta) * math.sin(phi) * math.sin(psi), -math.cos(psi) * math.sin(phi) - math.cos(phi) * math.cos(theta) * math.sin(psi), math.sin(theta) * math.sin(psi)],
                      [math.cos(theta) * math.cos(psi) * math.sin(phi) + math.cos(phi) * math.sin(psi), math.cos(phi) * math.cos(theta) * math.cos(psi) - math.sin(phi) * math.sin(psi), -math.cos(psi) * math.sin(theta)],
                      [math.sin(phi) * math.sin(theta), math.cos(phi) * math.sin(theta), math.cos(theta)]])
        #ZYZ Euler nach craig
        R = np.array([[math.cos(psi)*math.cos(theta)*math.cos(phi)-math.sin(psi)*math.sin(phi), -math.cos(psi)*math.cos(theta)*math.sin(phi)-math.sin(psi)*math.cos(phi), math.cos(psi)*math.sin(theta) ],
                      [math.sin(psi)*math.cos(theta)*math.cos(phi)+math.cos(psi)*math.sin(phi), -math.sin(psi)*math.cos(theta)*math.sin(phi)+math.cos(psi)*math.cos(phi), math.sin(psi)*math.sin(theta) ],
                      [-math.sin(theta)*math.cos(phi), math.sin(theta)*math.sin(phi), math.cos(theta)]])

        return R.transpose()
    
    def linear_acceleration(self, inputs, angles, xdot):
        gravity = np.array([[0], [0], [-self.drone.g]])
        R = self.rotation(angles)
        T = np.dot(R, self.drone.thrust(inputs))
        F_drag = -self.drone.kd * xdot
        a = gravity + (T + F_drag) / self.drone.m
        return a
        
    def angular_acceleration(self, inputs, omega):
        tau = self.drone.torques(inputs);
        omegaddot = np.dot(np.linalg.inv(self.drone.I), (tau - np.cross(omega.transpose(), np.dot(self.drone.I, omega).transpose()).transpose()));
        return omegaddot
    
    def thetadot2omega(self, thetadot, theta):
        R = np.array([[1, -math.sin(theta.item(1)), 0],
                      [0, math.cos(theta.item(0)), math.cos(theta.item(1)) * math.sin(theta.item(0))],
                      [0, -math.sin(theta.item(0)), math.cos(theta.item(1)) * math.cos(theta.item(0))]])
        omega = np.dot(R, thetadot)
        return omega
    
    def omega2thetadot(self, omega, theta):
        R = np.array([[1, -math.sin(theta.item(1)), 0],
                      [0, math.cos(theta.item(0)), math.cos(theta.item(1)) * math.sin(theta.item(0))],
                      [0, -math.sin(theta.item(0)), math.cos(theta.item(1)) * math.cos(theta.item(0))]])
        thetadot = np.dot(R.transpose(), omega)
        return thetadot
