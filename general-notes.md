# A few notes about computer vision tools

These notes were taken during last session with Safouane El Ghazouali.

- **deep anything 3**: model for predicting depth in a picture https://depth-anything-3.github.io/

- **sam2 ultralitycs**: segmentation model (follow the object shape precisely != bounding boxes) https://docs.ultralytics.com/models/sam-2/

- **Contrastive Difference Predictive Coding (CDPC)**: is a machine learning framework that combines contrastive learning with temporal prediction to learn representations from data with fewer training examples. It is often used to predict future states in time-series data or reinforcement learning environments by distinguishing the true future from randomly sampled "negative" examples.

- **intersection over union**: metric used to compute the bounding boxes prediction loss

- example notebook wit himage processing: https://colab.research.google.com/drive/16t6jTzo1mMSH0wi5a6U79utBNcMd0I03?usp=sharing

- **mmdetection**: toolbox library for detecting objects https://mmdetection.readthedocs.io/en/latest/. Alternative to ultralytics which is a very powerful, easy to use librairy, but which is expensive for business use (free for private (technology enthousiasts) and students use).

- **detectron2** from Meta: other alternative to ultralytics.


Concerning our bounding boxes flashing issue:
- reduce the confidence needed for a bounding box to be classified

- train on more data and more specific data exclusively

- try to do tracking https://github.com/abhiWriteCode/Object-Tracking or http://docs.opencv.org/3.4/d2/da2/classcv_1_1TrackerCSRT.html or https://learnopencv.com/object-tracking-using-opencv-cpp-python/.