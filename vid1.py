#Lane Detection
# =============================================================================
# References:
# https://theailearner.com/2018/10/15/creating-video-from-images-using-opencv-python/
# https://www.pyimagesearch.com/2016/03/07/transparent-overlays-with-opencv/
# =============================================================================
import cv2
import numpy as np
import os
import glob


 #Function for Hough Transform       
def HoughLines(segmented,threshold_intersections):
    print("houghlines")
    w,h=np.shape(segmented)
    Points=[]
   
    Points = np.argwhere(segmented == 255)
    
    diag_len=np.sqrt((w*w)+(h*h))

    accumulator=np.zeros((2*int(diag_len),360))               #defining a range from -maxdist to +maxdist 
    thetas=range(0,360)
    for p in Points:
        for t in thetas:
            r=round((p[1]*np.sin(np.deg2rad(t)))+(p[0]*np.cos(np.deg2rad(t)))+diag_len)        #shifing origin downward to get positive indexes
            accumulator[int(r)][int(t)]=accumulator[int(r)][int(t)]+1
        
    parameters=[]
    for i in range(len(accumulator)):
        for j in range(len(accumulator[0])):
            if accumulator[i][j]>threshold_intersections:
                parameters.append([i,j])                          #append r,theta
    
    print("endhogh")
    return parameters

# Function for Drawing lines
def draw_line(line,frame,height,width):
    rho,theta=line
    y1=height*3/4
    y2=height
    x1=(rho-(y1*np.sin(theta)))/np.cos(theta)
    x2=(rho-(y2*np.sin(theta)))/np.cos(theta)

    cv2.line(frame,(int(x1),int(y1)),(int(x2),int(y2)),(0,0,255),8)  
 
#funciton fro drawing convex polygon
def draw_poly(l1,l2,frame,height,width):
    rho,theta=l1
    y1=height*3/4
    y2=height
    x1=(rho-(y1*np.sin(theta)))/np.cos(theta)
    x2=(rho-(y2*np.sin(theta)))/np.cos(theta)
    rho,theta=l2
    y3=height*3/4
    y4=height
    x3=(rho-(y1*np.sin(theta)))/np.cos(theta)
    x4=(rho-(y2*np.sin(theta)))/np.cos(theta)
    pts = np.array([[x1,y1],[x2,y2],[x4,y4],[x3,y3]],dtype = np.int32)
    overlay = frame.copy()
    cv2.fillConvexPoly(overlay,pts,(0,255,0))
    opacity = 0.6
    return(cv2.addWeighted(frame, opacity, overlay, 1 - opacity, 0, overlay))

#Function to find the intersecting point of the lanes in image plane
def findIntersection(l1,l2):
    rho1,theta1=l1
    rho2,theta2=l2
    A=np.array([[np.cos(theta1),np.sin(theta1)],[np.cos(theta2),np.sin(theta2)]])
    B=np.transpose(np.array([rho1,rho2]))
    x=np.matmul(np.linalg.inv(A),B)
    return x
    
cap=cv2.VideoCapture("challenge_video.mp4")


flag=1 
old_leftLine=[]
old_rightLine=[]
old_intersection=[]
first_intersection=[]
c=0
op = cv2.VideoWriter('Output1.avi',cv2.VideoWriter_fourcc(*'DIVX'),25, (1280,720))
while 1:
    ret,frame=cap.read()
    #flag=0
    #cv2.imshow("f",frame)
    if frame is None:
        break
    height,width,layers=np.shape(frame)
    roi=np.zeros_like(frame)
    roi[int((height/2)+50):height,0:width]=frame[int((height/2)+50):height,0:width]
    
    gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    hsv=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    
   
    
    white=cv2.inRange(roi,np.array([200,200,200]),np.array([255,255,255]))
    yellow=cv2.inRange(hsv,np.array([20,100,100]),np.array([30,255,255]))
    
    full_detection=cv2.bitwise_or(white,yellow)
    mask_onimage = cv2.bitwise_and(gray, full_detection)
    de_noised = cv2.GaussianBlur(full_detection, (5,5), 0)
    kernel1=np.ones((3,3),np.uint8)
    de_noised=cv2.erode(de_noised,kernel1,iterations=1)
    
    
    
    edge=cv2.Canny(de_noised,50,100)
    #edge=cv2.Canny(edge,150,200)
   
    
    

    
    
    #cv2.imshow("white",white)
    #cv2.imshow("yellow",yellow)
    #cv2.imshow("fulld",full_detection)
    #cv2.imshow("mask_onimage",mask_onimage)
    cv2.imshow("denoised",de_noised)
    #cv2.imshow("edge",edge)

    
    #print(height,width)
    
    

    #lines=HoughLines(edge,50)               #r and theta for lines
    
    lines=cv2.HoughLines(edge,1,np.pi/180,55)
    
    #print(np.shape(lines))
    #cv2.imshow('mask',mask)
    
    
    left_lines=[]
    right_lines=[]
    
    
    
    if lines is not None:

        for r in lines:
            #print(np.rad2deg(r[0][1]))
            for rho ,theta in r:
                if np.rad2deg(theta)<70    and    np.rad2deg(theta)>10   :#<65    and   np.rad2deg(theta)>45:
                    left_lines.append([rho,theta])
                    print(np.rad2deg(theta))
                elif np.rad2deg(theta)>110:#115 and   np.rad2deg(theta)<145   :
                    right_lines.append([rho,theta])
                
                
                #print([rho,np.rad2deg(theta)])
        #for l in right_lines:
            #draw_line(l,frame,height,width)
            #cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),8)
                    
                
    
    
    leftLine=np.mean(left_lines, axis = 0 )            #axis =0 means along y axis
    rightLine=np.mean(right_lines, axis=0 )
    
    
    
    if np.shape(leftLine)==():
        draw_line(old_leftLine,frame,height,width)
        leftLine=old_leftLine
    
    else:
        #print([leftLine[0],np.rad2deg(leftLine[1])])
        old_leftLine=leftLine
        draw_line(leftLine,frame,height,width)
    
    if np.shape(rightLine)==():
        draw_line(old_rightLine,frame,height,width) 
        rightLine=old_rightLine
        
    else:
        #print([rightLine[0],np.rad2deg(rightLine[1])])
        old_rightLine=rightLine
        draw_line(rightLine,frame,height,width)
    frame = draw_poly(leftLine,rightLine,frame,height,width)        
    intersection=findIntersection(leftLine,rightLine)
    #print(intersection)
    if c==0:
        old_intersection=intersection
        first_intersection=intersection
    
    alpha=0.1
    intersection_=old_intersection+(alpha*(intersection-old_intersection))
    
    
    cv2.circle(frame,(int(intersection_[0]),int(intersection_[1])),3,(255,0,0),-1)
    
    max_x=first_intersection[0]+10#(width/2)+32
    min_x=first_intersection[0]-10#(width/2)+20
   
    
    # font 
    font = cv2.FONT_HERSHEY_SIMPLEX 
  
# org 
    org = (50, 50) 
  
# fontScale 
    fontScale = 1
   
# Blue color in BGR 
    color = (0, 255, 0) 
  
# Line thickness of 2 px 
    thickness = 3
    if intersection_[0]>max_x:
        frame = cv2.arrowedLine(frame, (int((width/2)-100),int(height/2)),  (int((width/2)+100),int(height/2)), 
                                         (0,255,0), 10)       #right arrow 
        frame = cv2.putText(frame, 'Steer Right', org, font,  fontScale, color, thickness, cv2.LINE_AA)
    elif intersection_[0]<min_x:
        frame = cv2.arrowedLine(frame,(int((width/2)+100),int(height/2)), (int((width/2)-100),int(height/2)),
                                         (0,255,0), 10)        #left arrow
        frame = cv2.putText(frame, 'Steer Left', org, font,  fontScale, color, thickness, cv2.LINE_AA)
    
    cv2.line(frame,(int(max_x),int(0)),(int(max_x),int(height)),(0,0,255),1)
    cv2.line(frame,(int(min_x),int(0)),(int(min_x),int(height)),(0,0,255),1)
    
    cv2.imshow("frame",frame)

    Out_vid=[]
    Out_vid.append(frame)
    
    

    
        
    old_intersection=intersection_
    op.write(frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
    c=c+1
    


op.release()
cap.release()

cv2.destroyAllWindows()
    