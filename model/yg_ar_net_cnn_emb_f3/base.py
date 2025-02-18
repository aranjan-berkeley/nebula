import pandas as pd
import torch
import sqlite3
import re
import os
import os.path as osp

from nebula.common import get_device
from nebula.data.yg_ar.setup_data_f3 import setup_data
from nebula.model.yg_ar_net_cnn_emb_f3.component.encoder import Encoder
from nebula.model.yg_ar_net_cnn_emb_f3.component.decoder import Decoder
from nebula.model.yg_ar_net_cnn_emb_f3.component.seq2seq import Seq2Seq


class ygarNetCNNEMBF3:
    def __init__(
            self,
            df_path,
            batch_size=128,
    ):
        self.device = get_device()

        (
            self.train_dl,
            self.validation_dl,
            self.test_dl,
            self.train_dl_small,
            self.label_vocab,
            self.embedding_shape
        ) = setup_data(
            df_path=df_path,
            batch_size=batch_size,
        )

        OUTPUT_DIM = len(self.label_vocab.vocab)
        HID_DIM = 28 # it equals to embedding dimension
        EMBEDDING_SIZE = 56
        ENC_LAYERS = 3
        DEC_LAYERS = 3
        ENC_HEADS = 4
        DEC_HEADS = 4
        ENC_PF_DIM = 56
        DEC_PF_DIM = 56
        ENC_DROPOUT = 0.1
        DEC_DROPOUT = 0.1
        MAX_LENGTH = 128

        enc = Encoder(
            embedding_shape=self.embedding_shape,
            hid_dim=HID_DIM,
            n_layers=ENC_LAYERS,
            n_heads=ENC_HEADS,
            pf_dim=ENC_PF_DIM,
            dropout=ENC_DROPOUT,
            device=self.device,
            max_length=MAX_LENGTH,
            embedding_size=EMBEDDING_SIZE
        )

        dec = Decoder(OUTPUT_DIM,
                      HID_DIM,
                      DEC_LAYERS,
                      DEC_HEADS,
                      DEC_PF_DIM,
                      DEC_DROPOUT,
                      self.device,
                      MAX_LENGTH
                      )

        self.TRG_PAD_IDX = self.label_vocab.get_stoi()["<pad>"]

        self.model = Seq2Seq(
            enc,
            dec,
            self.TRG_PAD_IDX,
            self.device
        ).to(self.device)

    def load_model(self, trained_model_path):
        self.model.load_state_dict(
            torch.load(
                trained_model_path,
                map_location=self.device
            )
        )
