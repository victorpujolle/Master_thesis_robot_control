import numpy as np


class Generator():
    """
    This class is used for all kinematics calculation of the arm
    """

    def __init__(self, L, Q_MIN, Q_MAX):
        """
        init the const value of the arm
        :param L: length of each links
        :param Q_MIN: values of each q_min for each links (unit : rad)
        :param Q_MAX: values of each q_max for each links (unit : rad)
        """
        self.L = L
        self.Q_MIN = Q_MIN
        self.Q_MAX = Q_MAX

        self.T0 = np.eye(4)
        self.T1 = np.eye(4)
        self.T2 = np.eye(4)
        self.T3 = np.eye(4)
        self.T4 = np.eye(4)
        self.T5 = np.eye(4)

    # basic 3D matrix generator
    def Trans(self, x, y, z):
        return np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ])
    def RotX(self, alpha):
        return np.array([
            [ 1 ,       0        ,        0        , 0 ],
            [ 0 , math.cos(alpha), -math.sin(alpha), 0 ],
            [ 0 , math.sin(alpha),  math.cos(alpha), 0 ],
            [ 0 ,       0        ,        0        , 1 ]
        ])
    def RotY(self, beta):
        return np.array([
            [  math.cos(beta), 0 , math.sin(beta), 0 ],
            [       0        , 1 ,      0        , 0 ],
            [ -math.sin(beta), 0 , math.cos(beta), 0 ],
            [       0        , 0 ,      0        , 1 ]
        ])
    def RotZ(self, gamma):
        return np.array([
            [ math.cos(gamma), -math.sin(gamma), 0 , 0 ],
            [ math.sin(gamma),  math.cos(gamma), 0 , 0 ],
            [       0        ,        0        , 1 , 0 ],
            [       0        ,        0        , 0 , 1 ]
        ])

    # transfert matrices
    def compute_T0(self,q0):
        ct = np.cos(q0)
        st = np.sin(q0)

        self.T0[0, 0] =  ct
        self.T0[0, 1] = -st
        self.T0[1, 0] =  st
        self.T0[1, 1] =  ct
        self.T0[0, 3] = 0
        self.T0[1, 3] = 0
        self.T0[2, 3] = self.L[0]

        return self.T0
    def compute_T1(self,q1):
        ct = np.cos(q1)
        st = np.sin(q1)

        self.T1[0, 0] = ct
        self.T1[0, 2] = st
        self.T1[2, 0] =-st
        self.T1[2, 2] = ct
        self.T1[0, 3] = self.L[1] * ct
        self.T1[1, 3] = 0
        self.T1[2, 3] = self.L[1]* st

        return self.T1
    def compute_T2(self,q2):
        ct = np.cos(q2)
        st = np.sin(q2)

        self.T2[1, 1] =  ct
        self.T2[1, 2] = -st
        self.T2[2, 1] =  st
        self.T2[2, 2] =  ct
        self.T2[0, 3] = self.L[2]
        self.T2[1, 3] = 0
        self.T2[2, 3] = 0

        return self.T2
    def compute_T3(self,q3):
        ct = np.cos(q3)
        st = np.sin(q3)

        self.T3[0, 0] =  ct
        self.T3[0, 2] =  st
        self.T3[2, 0] = -st
        self.T3[2, 2] =  ct
        self.T3[0, 3] = self.L[3] * ct
        self.T3[1, 3] = 0
        self.T3[2, 3] = self.L[3] * st

        return self.T3
    def compute_T4(self,q4):
        ct = np.cos(q4)
        st = np.sin(q4)

        self.T4[1, 1] =  ct
        self.T4[1, 2] = -st
        self.T4[2, 1] =  st
        self.T4[2, 2] =  ct
        self.T4[0, 3] = self.L[4]
        self.T4[1, 3] = 0
        self.T4[2, 3] = 0

        return self.T4
    def compute_T5(self,q5):
        ct = np.cos(q5)
        st = np.sin(q5)

        self.T5[0, 0] =  ct
        self.T5[0, 2] =  st
        self.T5[2, 0] = -st
        self.T5[2, 2] =  ct
        self.T5[0, 3] = self.L[5] * ct
        self.T5[1, 3] = 0
        self.T5[2, 3] = self.L[5] * st

        return self.T5
    def compute_T_sh(self, q0, q1):
        # shoulder
        return np.dot(self.compute_T0(q0), self.compute_T1(q1))
    def compute_T_el(self, q0, q1, q2, q3):
        # elbow
        return np.dot(np.dot(self.compute_T_sh(q0, q1), self.compute_T2(q2)),self.compute_T3(q3))
    def compute_T_wr(self, q0, q1, q2, q3, q4, q5):
        # wrest
        return np.dot(np.dot(self.compute_T_el(q0, q1, q2, q3), self.compute_T4(q4)),self.compute_T5(q5))

    # transfert matrices computation with DH parameters
    def calculate_DH_param(self, q):
        """
        Initialisation of the DH parameters of the arm (change this function for your arm)
        :param q: the q parameters of your arm, here the angle of each joints
        """
        self.DH_parameters = np.array([
            [self.L[0], q[0], 0 , 0],
            [0, q[1], self.L[1], np.pi / 2],
            [self.L[2], q[2], 0, 0],
            [0, q[3], self.L[3], np.pi / 2],
            [self.L[4], q[4], 0, 0],
            [0, q[5], self.L[5], np.pi / 2],
        ])

        return 0
    def calculate_T(self, d, theta, r, alpha):
        """
        calculate the Denavit and Hartenberg matrix for a joint
        :param d: link offset
        :param r: link length
        :param alpha: link twist
        :param theta: link angle
        :return: the Denavit and Hartenberg matrix
        """
        T = np.zeros((4,4))

        ct, st, ca, sa = 0, 0, 0, 0

        if  round(theta, 5) == 0: # zero case
            ct = 1
            st = 0
        elif round(theta, 5) == round(np.pi / 2, 5): # pi/2 case
            ct = 0
            st = 1
        elif round(theta, 5) == round(np.pi, 5):  # pi case
            ct = -1
            st = 0
        elif round(theta, 5) == round(3 * np.pi / 2, 5):  # 3pi/2 case
            ct = 0
            st = -1
        else: # general case
            ct = np.cos(theta)
            st = np.sin(theta)

        if round(alpha, 5) == 0: # zero case
            ca = 1
            sa = 0
        elif round(alpha, 5) == round(np.pi/2, 5): # pi/2 case
            ca = 0
            sa = 1
        elif round(alpha, 5) == round(np.pi, 5):  # pi case
            ca = -1
            sa = 0
        elif round(alpha, 5) == round(3 * np.pi / 2, 5):  # 3pi/2 case
            ca = 0
            sa = -1
        else: # general case
            ca = np.cos(alpha)
            sa = np.sin(alpha)

        # rotation, first line
        T[0, 0] = ct
        T[0, 1] = - st * ca
        T[0, 2] = st * sa

        # rotation second line
        T[1, 0] = st
        T[1, 1] = ct * ca
        T[1, 2] = - ct * sa

        # rotation last line
        T[2, 1] = sa
        T[2, 2] = ca

        # translation
        T[0, 3] = r * ct
        T[1, 3] = r * st
        T[2, 3] = d

        # last value
        T[3, 3] = 1

        return T

    # forward kinematic computation
    def compute_FK(self, q):
        """
        Compute the forward kinematics of the arm
        :param q: the angle of each joint
        :return: the final rotation matrix and translation
        """
        T = self.compute_T_wr(q[0],q[1],q[2],q[3],q[4],q[5])
        R = T[0:3,0:3]
        t = T[0:3,3]
        print('T : \n',T)
        print('R : \n',R)
        print('t : \n',t)

    # pose computation for drawing
    def ini_pose(self, q):






