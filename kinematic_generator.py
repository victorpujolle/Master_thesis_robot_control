import numpy as np


class Generator():
    """
    This class is used for all kinematics calculation of the arm
    """

    def __init__(self, L, OFFSET, ORIGIN_TRANS, Q_MIN, Q_MAX):
        """
        init the const value of the arm
        :param L: length of each links
        :param Q_MIN: values of each q_min for each links (unit : rad)
        :param Q_MAX: values of each q_max for each links (unit : rad)
        """
        self.L = L
        self.OFFSET = OFFSET
        self.ORIGIN_TRANS = ORIGIN_TRANS
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
            [ 0 , np.cos(alpha), -np.sin(alpha), 0 ],
            [ 0 , np.sin(alpha),  np.cos(alpha), 0 ],
            [ 0 ,       0        ,        0        , 1 ]
        ])
    def RotY(self, beta):
        return np.array([
            [  np.cos(beta), 0 , np.sin(beta), 0 ],
            [       0        , 1 ,      0        , 0 ],
            [ -np.sin(beta), 0 , np.cos(beta), 0 ],
            [       0        , 0 ,      0        , 1 ]
        ])
    def RotZ(self, gamma):
        return np.array([
            [ np.cos(gamma), -np.sin(gamma), 0 , 0 ],
            [ np.sin(gamma),  np.cos(gamma), 0 , 0 ],
            [       0        ,        0        , 1 , 0 ],
            [       0        ,        0        , 0 , 1 ]
        ])

    '''Transformation matrix of each joint & certain part'''

    def compute_T0(self):
        # return self.RotY(math.pi/2) @ self.Trans(0,0,-self.L[0])
        #self.T0 = self.RotY(np.pi / 2).dot(self.Trans(0, 0, self.L[0]))
        self.T0 = self.Trans(self.ORIGIN_TRANS[0], self.ORIGIN_TRANS[1], self.ORIGIN_TRANS[2] + self.L[0])
        return self.T0

    def compute_T1(self, q1):
        # return self.RotZ(q1) @ self.Trans(0,0,-self.L[1]) @ self.RotX(math.pi/2)
        self.T1 = self.RotZ(q1).dot(self.Trans(0, 0, 0).dot(self.RotX(np.pi / 2)))
        return self.T1

    def compute_T2(self, q2):
        self.T2 = self.RotZ(q2 + np.pi / 2).dot(self.Trans(0, 0, 0).dot(self.RotX(np.pi / 2)))
        #self.T2 = self.RotZ(q2).dot(self.Trans(self.L[1],0,0))
        return self.T2

    def compute_Tel(self): # elbow
        self.T_el = self.Trans(0, 0, self.L[1] + self.L[2])
        return self.T_el

    def compute_T3(self, q3):
        self.T3 = self.RotZ(q3 + np.pi / 2).dot(self.Trans(0, 0, 0).dot(self.RotX(np.pi / 2)))
        return self.T3

    def compute_T4(self, q4):
        self.T4 = self.RotZ(q4).dot(self.Trans(0, 0, 0).dot(self.RotX(-np.pi / 2)))
        return self.T4

    def compute_Twr(self):  # wrest
        self.T_wr = self.RotZ(-np.pi / 2).dot(self.Trans(0, 0, self.L[3] + self.L[4]))
        return self.T_wr

    def compute_T5(self, q5):
        self.T5 = self.RotZ(q5).dot(self.Trans(0, 0, 0).dot(self.RotX(-np.pi / 2)))
        return self.T5

    def compute_T6(self, q6):
        self.T6 = self.RotZ(q6).dot(self.Trans(0, 0, 0).dot(self.RotX(np.pi / 2).dot(self.RotZ(-np.pi / 2))))
        return self.T6

    def compute_Teef(self):  # end effector
        self.T_eef = self.Trans(0, 0, self.L[5])
        return self.T_eef

    ''' Transformation matrix from global coordinate to an certain part'''

    def compute_T0_sh(self, q1, q2):  # shoulder
        self.Tglobal2sh =  self.compute_T0().dot(self.compute_T1(q1).dot(self.compute_T2(q2)))
        return self.Tglobal2sh

    def compute_T0_el(self, q1, q2, q3, q4):  # elbow
        self.Tglobal2el = self.compute_T0_sh(q1, q2).dot(self.compute_Tel().dot(self.compute_T3(q3).dot(self.compute_T4(q4))))
        return self.Tglobal2el

    def compute_T0_wr(self, q1, q2, q3, q4, q5, q6):  # wrest
        self.Tglobal2wr = self.compute_T0_el(q1, q2, q3, q4).dot(self.compute_Twr().dot(self.compute_T5(q5).dot(self.compute_T6(q6))))
        return self.Tglobal2wr

    def compute_T0_eef(self, q1, q2, q3, q4, q5, q6):  # end effector
        self.Tglobal2eef = self.compute_T0_wr(q1, q2, q3, q4, q5, q6).dot(self.compute_Teef())
        return self.Tglobal2eef


    # toolkit for homogenous coordinates
    def homogenous2space(self,v):
        """
        project the homogenous vector v to the projective space in 3D
        :param v: homogenous vector
        :return: projected vector
        """
        return np.array([v[0]/v[3], v[1]/v[3], v[2]/v[3]])

    def space2homogenous(self,v):
        """
        project of 3D point into the homogenous considering it is not at the infinity
        :param v: 3D vector
        :return: projected homogenous vector
        """
        return np.array([v[0], v[1], v[2], 1])

    def homo_add(self,v,w):
        """
        add two homogenous vectors
        :param v: vector
        :param w: vector
        :return: v + w
        """
        return self.space2homogenous(self.homogenous2space(v) + self.homogenous2space(w))

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
        T = self.compute_T0_eef(q[0],q[1],q[2],q[3],q[4],q[5])
        R = T[0:3,0:3]
        t = T[0:3,3]

        return R, t

    # pose computation for drawing
    def compute_pose(self, q):
        """
        Compute the position of each joints
        :param q: the angle of each joint
        :return: the list of x, y, z coord of each joint
        """
        joint_pos_init = np.array([0,0,0,1])
        #self.compute_T_wr(q[0], q[1], q[2], q[3], q[4], q[5])
        self.compute_T0_eef(q[0], q[1], q[2], q[3], q[4], q[5]) # will compute all the transformation matrices

        origin = self.Trans(0, 0, 0)[0:3, -1]
        T0_sh  = self.compute_T0_sh(q[0], q[1])[0:3, -1]
        T0_el  = self.compute_T0_el(q[0], q[1], q[2], q[3])[0:3, -1]
        T0_wr  = self.compute_T0_wr(q[0], q[1], q[2], q[3], q[4], q[5])[0:3, -1]
        T0_eef = self.compute_T0_eef(q[0], q[1], q[2], q[3], q[4], q[5])[0:3, -1]

        x = [0, T0_sh[0], T0_el[0], T0_wr[0], T0_eef[0]]
        y = [0, T0_sh[1], T0_el[1], T0_wr[1], T0_eef[1]]
        z = [0, T0_sh[2], T0_el[2], T0_wr[2], T0_eef[2]]

        return x,y,z

    def compute_ref(self,q):
        """
        Compute all the local referencial to help the visualisation of the arm
        :param q: the angle of each joint
        :return: the list with all the referencials
        """
        # base vectors
        origin = np.array([0, 0, 0 ,1])
        x_base = np.array([1, 0, 0, 1])
        y_base = np.array([0, 1, 0, 1])
        z_base = np.array([0, 0, 1, 1])

        # base ref to draw
        ref0 = np.array([origin, x_base, y_base, z_base]).T
        ref1 = self.T0.dot(ref0)
        ref2 = self.T1.dot(ref1)
        ref3 = self.T2.dot(ref2)
        ref4 = self.T3.dot(ref3)
        ref5 = self.T4.dot(ref4)
        ref6 = self.T5.dot(ref5)

        list_ref = np.array([ref0, ref1, ref2, ref3, ref4, ref5, ref6])

        return list_ref




