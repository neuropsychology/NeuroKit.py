## CURRENT : 0.1.7 

### Breaking changes
- `ecg_wave_detector()`: removed the plot parameter [#22](https://github.com/neuropsychology/NeuroKit.py/pull/21)
### New functions
- Added new QRS segmenter (pekkanen) method [#22](https://github.com/neuropsychology/NeuroKit.py/pull/21)
### Major changes
### Minor changes
- Better separation between `ecg_preprocess` and `ecg_process` (and short vs long computation processes) [#21](https://github.com/neuropsychology/NeuroKit.py/pull/21)
- Completely Separated bio_ecg and bio_ecg_preprocessing files [#22](https://github.com/neuropsychology/NeuroKit.py/pull/21)
---------
## 0.1.6 

### Breaking changes
- `indentify_outliers` changed to `find_outliers` to start creating some coherence in the API (using prefixes like `find_`, `read_`, `compute_`, `process_`, `plot_` etc.) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
### New functions
### Major changes
- Introducing CHANGELOG [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
### Minor changes
- Added segmenter choice option for ecg processing [#20](https://github.com/neuropsychology/NeuroKit.py/pull/20)
- Improved CONTRIBUTING.md [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Structural changes [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Increase tests [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)


