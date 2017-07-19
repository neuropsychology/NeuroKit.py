## NEXT : 0.2

- Focus: EEG processing

---------

## CURRENT : 0.1

### Breaking changes
- `ecg_wave_detector()`: removed the plot parameter [#22](https://github.com/neuropsychology/NeuroKit.py/pull/22)
- `indentify_outliers` changed to `find_outliers` to start creating some coherence in the API (using prefixes like `find_`, `read_`, `compute_`, `process_`, `plot_` etc.) (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19) 
### New functions / parameters
- Added new QRS segmenter (pekkanen) method (**since 0.1.7**) [#22](https://github.com/neuropsychology/NeuroKit.py/pull/22)
### Major changes
- Enhanced HRV processing: computes HRV frequency domain power over time (**since 0.1.8**) [#24](https://github.com/neuropsychology/NeuroKit.py/pull/24)
### Minor changes
- Introducing CHANGELOG (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Better separation between `ecg_preprocess` and `ecg_process` (and short vs long computation processes) (**since 0.1.7**) [#21](https://github.com/neuropsychology/NeuroKit.py/pull/21)
- Completely Separated bio_ecg and bio_ecg_preprocessing files (**since 0.1.7**) [#22](https://github.com/neuropsychology/NeuroKit.py/pull/22)
- Added segmenter choice option for ecg processing (**since 0.1.6**) [#20](https://github.com/neuropsychology/NeuroKit.py/pull/20)
- Improved CONTRIBUTING.md (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Structural changes (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Increase tests (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)


