from tensorflow.keras.layers import Input, Reshape, Conv2D, BatchNormalization
from tensorflow.keras.layers import MaxPool2D, Dropout, Permute, Flatten, Dense
from tensorflow.keras.models import Model
import os
import numpy as np

MODEL_SRATE = 16000
CENTS_MAPPING = np.linspace(0, 7180, 360) + 1997.3794084376191

def init(model_capacity, package_dir):
  global model
  print('Loading model...')

  capacity_multiplier = {
      'tiny': 4, 'small': 8, 'medium': 16, 'large': 24, 'full': 32
  }[model_capacity]

  layers = [1, 2, 3, 4, 5, 6]
  filters = [n * capacity_multiplier for n in [32, 4, 4, 4, 8, 16]]
  widths = [512, 64, 64, 64, 64, 64]
  strides = [(4, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)]

  x = Input(shape=(1024,), name='input', dtype='float32')
  y = Reshape(target_shape=(1024, 1, 1), name='input-reshape')(x)

  for l, f, w, s in zip(layers, filters, widths, strides):
      y = Conv2D(f, (w, 1), strides=s, padding='same',
                  activation='relu', name="conv%d" % l)(y)
      y = BatchNormalization(name="conv%d-BN" % l)(y)
      y = MaxPool2D(pool_size=(2, 1), strides=None, padding='valid',
                    name="conv%d-maxpool" % l)(y)
      y = Dropout(0.25, name="conv%d-dropout" % l)(y)

  y = Permute((2, 1, 3), name="transpose")(y)
  y = Flatten(name="flatten")(y)
  y = Dense(360, activation='sigmoid', name="classifier")(y)

  model = Model(inputs=x, outputs=y)

  # package_dir = os.path.dirname(os.path.realpath(__file__))
  filename = "model-{}.h5".format(model_capacity)
  model.load_weights(os.path.join(package_dir, filename))
  model.compile('adam', 'binary_crossentropy')

  print('Model loaded.')

def get_activation(y, sr):
  if sr != MODEL_SRATE:
    print('Sample rate incorrect')
    raise Exception()
  assert len(y) == 1024

  # normalize each frame -- this is expected by the model
  y -= np.mean(y)
  y /= np.std(y)

  # run prediction and convert the frequency bin weights to Hz
  return model.predict(y[None, :])[0]

def to_local_average_cents(salience):
  center = int(np.argmax(salience))
  start = max(0, center - 4)
  end = min(len(salience), center + 5)
  salience = salience[start:end]
  product_sum = np.sum(
    salience * CENTS_MAPPING[start:end])
  weight_sum = np.sum(salience)
  return product_sum / weight_sum

def estimateF0(frame, frame_len, sr):
  activation = get_activation(frame, sr)
  # confidence = activation.max()
  cents = to_local_average_cents(activation)
  frequency = 10 * 2 ** (cents / 1200)
  return frequency
