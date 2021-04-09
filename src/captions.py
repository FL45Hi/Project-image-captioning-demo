"""
programmer : fl45h
"""

import glob
import re
from keras.applications.vgg16 import VGG16
from keras.models import Model, load_model
from keras.preprocessing import image
from PIL import Image
import numpy as np
import pickle

from keras.preprocessing import sequence
#from keras.layers import Input, Dense, Embedding, Dropout, LSTM, add, RepeatVector, Activation, TimeDistributed, Bidirectional, Add
# from keras.optimizers import RMSprop, Adam
from keras.models import Model
from keras.utils import plot_model
from keras.models import Sequential
from keras.utils import plot_model

import warnings
warnings.filterwarnings("ignore")

model = load_model("model_4.h5")

def VGG():
    model = VGG16(weights='imagenet')
    
    model_input = model.input
    model_output = model.layers[-2].output      #Choosing the output of 2nd last layer, FC 4096
    
    model = Model(inputs = model_input, outputs = model_output)
    return model

VGG_model = VGG()


vocab = pickle.load(open("/src/new_vocabulary.p", 'rb'))
vocab_size = len(vocab)

def word_index(vocab):
    t = {}
    for i, j in enumerate(vocab):
        t[j] = i
        
    return t

index = word_index(vocab)
index['<start>'], index["<stop>"]

def input_preprocess(path):
    imag = image.load_img(path, target_size=(224, 224))
    x = image.img_to_array(imag)
    x = x.reshape((1, x.shape[0], x.shape[1], x.shape[2]))
    x /= 255
    x -= 0.5
    x *= 2
    return x

def encode_image(path):
    img = input_preprocess(path)
    encoded = VGG_model.predict(img)
    encoded = np.reshape(encoded, encoded.shape[1])
    #feature_vector = model_resnet.predict(img)
    #feature_vector = feature_vector.reshape(1, feature_vector.shape[1])
    #return feature_vector
    return encoded

index_word ={}
for i,j in index.items():
    
    index_word[j] = i


def predict_caption(photo):
    begin_cap = ["<start>"]
    # in_text = "startseq"
    max_caption_length = 37
    while True:
        partial_caption = [index[i] for i in begin_cap]
        partial_caption = sequence.pad_sequences([partial_caption], maxlen=max_caption_length, padding='post')
        #encode = encoded_test_image[image[len(all_images_dir):]]
        ypred =  model.predict([np.array([photo]), np.array(partial_caption)])
        #preds = model.predict([np.array([encode]), np.array(partial_caption)])
        word_prediction = index_word[np.argmax(ypred[0])]
        begin_cap.append(word_prediction)
        
        if word_prediction == "<stop>" or len(begin_cap) > max_caption_length:
            break


    # return final_caption
    final_caption =  ' '.join(begin_cap[1:-1])
    final_caption = final_caption.capitalize() + "."
    return final_caption

def gen_caption(pic): 

    photo = encode_image(pic)
    
    caption = predict_caption(photo)
    # keras.backend.clear_session()
    return caption


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, required=True, help='input image for generating caption')
    parser.add_argument('-m', '--model_path', type=str, default='src/model_4.h5', help='path for trained model')
    #parser.add_argument('--vocab_path', type=str, default='src/vocab/vocab.json', help='path for vocabulary wrapper')

    args = parser.parse_args()
    gen_caption(args)