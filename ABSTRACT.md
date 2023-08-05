The authors of the **KolektorSDD2** dataset highlight the importance of surface-quality inspection in industrial production processes. They point out that in large-scale production, the occurrence of defective items is significantly lower than non-defective ones, leading to a heavily skewed ratio. This scarcity of defective samples poses challenges for supervised deep-learning methods that require a large set of annotated samples to learn specific defect characteristics.

The authors also emphasize the difficulty in producing detailed annotations, especially pixel-level annotations that are essential for differentiating anomalous image regions from regular ones accurately. Creating accurate pixel-level annotations is tedious and costly, particularly when defining boundaries between defects and regular surface appearance is challenging. To address these challenges, the authors aim to minimize the labeling effort by reducing the required number of annotations and improving label precision.

The dataset KolektorSDD2 used in the study consists of color images of defective production items captured with a visual inspection system. These images were provided and partially annotated by the industrial partner Kolektor Group d.o.o. The dataset includes images of approximately 230 pixels wide and 630 pixels high, captured in a controlled environment. It is divided into train and test subsets, with 2085 negative and 246 positive samples in the train set, and 894 negative and 110 positive samples in the test set. Defects in the dataset are annotated with fine-grained segmentation masks and vary in shape, size, and color, ranging from small scratches and minor spots to large surface imperfections.