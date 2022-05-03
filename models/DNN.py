import tensorflow as tf
import keras
import json
import os

from keras import layers
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix

import sys
sys.path.append("..")
from configure import Config
from utils import *


# build model
def DNN_scr(input_shape, cfg):
    model = keras.Sequential()
    model.add(layers.Dense(units=cfg.units_h1, input_dim=input_shape, activation='relu'))
    model.add(layers.Dense(units=cfg.units_h2, activation='relu'))
    model.add(layers.Dense(units=cfg.units_h3, activation='relu'))
    model.add(layers.Dense(units=cfg.units_h4, activation='relu'))
    model.add(layers.Dense(cfg.num_class, activation='softmax'))

    print(model.summary())

    return model


if __name__ == "__main__":
    cfg = Config()

    # setup parameter based on the data source
    if cfg.raw_data_source == True:
        X_train, X_test, y_train, y_test = load_raw_data(cfg.raw_aursad_path, expand_flag=False)
        model_path = os.path.join(cfg.model_DNN_path, 'raw_model.h5')
        loss_img = os.path.join(cfg.DNN_loss_acc_fig_path, 'raw_loss.png')
        acc_img = os.path.join(cfg.DNN_loss_acc_fig_path, 'raw_acc.png')
        precision = "raw_DNN_precision"
        recall = "raw_DNN_recall"
        f1 = "raw_DNN_f1"
    else:
        X_train, X_test, y_train, y_test = load_feature_data(cfg.feature_aursad_path, expand_flag=False)
        model_path = os.path.join(cfg.model_DNN_path, 'feature_model.h5')
        loss_img = os.path.join(cfg.DNN_loss_acc_fig_path, 'feature_loss.png')
        acc_img = os.path.join(cfg.DNN_loss_acc_fig_path, 'feature_acc.png')
        precision = "feature_DNN_precision"
        recall = "feature_DNN_recall"
        f1 = "feature_DNN_f1"

    # construct DNN
    model = DNN_scr(X_train.shape[1], cfg)
    #
    # compile model
    opt = tf.optimizers.Adam(cfg.lr)
    model.compile(optimizer=opt, loss=cfg.loss, metrics='acc')

    # the training will stop if the accuracy is not improved after "patinence" epochs - using early stopping for efficient
    callbacks = [keras.callbacks.EarlyStopping(patience=cfg.patience, restore_best_weights=True)]

    # training model
    history = model.fit(X_train, y_train, epochs=cfg.epochs, batch_size=cfg.batch_size, validation_data=(X_test,y_test), callbacks=callbacks)

    # save model
    model.save(model_path)

    # plot the acc and loss
    plot_loss_acc(history, loss_img, acc_img)

    # get f1, precision and recall scores
    model = keras.models.load_model(model_path)

    y_pred1 = model.predict(X_test)
    y_pred = np.argmax(y_pred1, axis=1)

    # save f1, precision, and recall scores
    scores = {precision: precision_score(y_test, y_pred, average="macro"),
              recall: recall_score(y_test, y_pred, average="macro"),
              f1: f1_score(y_test, y_pred, average="macro")}
    with open(cfg.scores_file_path, 'a') as outfile:
        json.dump(scores, outfile)
    outfile.close()

