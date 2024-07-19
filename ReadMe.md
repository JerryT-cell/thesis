**Extraction of UML models from xmi files**

The extraction is done by randomly removing classes and attributes from the xmi files.
Attributes in each class are removed with a probability of 0.7. Classes are removed with a probability of 0.3.


**Fine-tuning of the models**
Two models are used for finetuning
1. BERT



2. Mistral
The fine-tuning is done by training the model on the dataset with the extracted models and then testing the model on the original dataset. The model is trained for 10 epochs with a batch size of 32. The learning rate is set to 0.0001. The model is trained on a single NVIDIA Tesla V100 GPU.