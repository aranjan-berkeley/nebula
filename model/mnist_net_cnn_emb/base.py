import pandas as pd
import torch
import sqlite3
import re
import os
import os.path as osp

from nebula.common import get_device
from nebula.data.mnist_seq.setup_data import setup_data
from nebula.model.mnist_net_cnn_emb.component.encoder import Encoder
from nebula.model.mnist_net_cnn_emb.component.decoder import Decoder
from nebula.model.mnist_net_cnn_emb.component.seq2seq import Seq2Seq


class mnistNetCNNEMB:
    def __init__(
            self,
            trained_model_path=None,
            batch_size=128,
            location="~/data"
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
            batch_size=batch_size,
            location=location
        )

        OUTPUT_DIM = len(self.label_vocab.vocab)
        HID_DIM = 20  # it equals to embedding dimension
        ENC_LAYERS = 3
        DEC_LAYERS = 3
        ENC_HEADS = 2
        DEC_HEADS = 2
        ENC_PF_DIM = 50
        DEC_PF_DIM = 50
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
            embedding_size=40
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
        self.model.eval()
