# -*- coding: utf-8 -*-
"""
Example Script for Reading EEG data for the course available at: http://neurotoolspy.readthedocs.io/en/latest/tutorials/EEG.html#reading-data
Authors: Makowski et al. (2016)
Copyright: L'École de Neuropsychologie
Site: https://github.com/neuropsychology/NeuroTools.py
"""
import neurotools as nt

raw = nt.load_raw(example_participant,
               path="Data/",
               reference=['TP7', 'TP9'],
               eog=('HEOG', 'VEOG'),
               misc=['PHOTO'])

