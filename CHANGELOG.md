## Dev 

### Breaking changes
- Change name of `discrete_to_continuous` to `interpolate`
- Remove "nonlinear" from `ecg_hrv_features` from `ecg_process` and `bio_process`
### New functions / parameters
- Added "ecg_simulate"
### Major changes



## 0.2

### Breaking changes
- Append "complexity_" to all complexity function names (e.g., `entropy_shannon` -> `complexity_entropy_shannon`) (**since 0.2.0**) [#32](https://github.com/neuropsychology/NeuroKit.py/pull/32)
- `read_acqknowledge` new parameter, `return_sampling_rate`. Default to False to keep old behaviour, but default will be changed to True in the future (**since 0.2.0**) [#32](https://github.com/neuropsychology/NeuroKit.py/pull/32)


### New functions / parameters
- `ecg_signal_quality`: Added rpeak parameter and returns an interpolated array of signal quality [#35](https://github.com/neuropsychology/NeuroKit.py/pull/35)
- `eeg_complexity`: First attempt to compute complexity features of epochs (**since 0.2.0**) [#32](https://github.com/neuropsychology/NeuroKit.py/pull/32)
- `emg_process`: Computes linear envelope and activation (**since 0.2.0**) [#32](https://github.com/neuropsychology/NeuroKit.py/pull/32)
- `staircase`: Add a routine for staircase procedures used in psychophysics [#55](https://github.com/neuropsychology/NeuroKit.py/pull/55)

### Major changes


### Minor changes
- Fix bug when unpickling, througk `read_nk_object`, a dataframe built with pandas < 0.17 [#42](https://github.com/neuropsychology/NeuroKit.py/pull/42)
- Refactor testing structure [#41](https://github.com/neuropsychology/NeuroKit.py/pull/41)
- `plot_events_in_signal`: Changed `events` parameter to `events_onsets` [#41](https://github.com/neuropsychology/NeuroKit.py/pull/41)
- Fixed a line in ecg_hrv so that it works if the provided rpeaks are array instead of list [#36](https://github.com/neuropsychology/NeuroKit.py/pull/36)
- Taking interest in BVP
- Fixed ecg_process for sampling rate superior to 1000 Hz [#35](https://github.com/neuropsychology/NeuroKit.py/pull/35)
- Added [scripts](https://github.com/neuropsychology/NeuroKit.py/tree/master/utils/ecg_signal_quality_model_creation) for ECG signal quality model creation [#35](https://github.com/neuropsychology/NeuroKit.py/pull/35)
- Started documenting ECG signal quality in docs [#35](https://github.com/neuropsychology/NeuroKit.py/pull/35)
- Fixed bug in `ecg_hrv`
- Moved `find_closest_in_list` and `find_following_duplicates` from miscellaenous to statistics [#55](https://github.com/neuropsychology/NeuroKit.py/pull/55)


## 0.1

### Breaking changes
- EventRelated functions for biosignals: complete overhaul (**since 0.1.93**) [#30](https://github.com/neuropsychology/NeuroKit.py/pull/30)
- `eda_process()`: Completely refactored that function,  removed many parameters. (**since 0.1.92**) [#29](https://github.com/neuropsychology/NeuroKit.py/pull/29)
- `ecg_wave_detector()`: removed the plot parameter (**since 0.1.7**) [#22](https://github.com/neuropsychology/NeuroKit.py/pull/22)
- `indentify_outliers` changed to `find_outliers` to start creating some coherence in the API (using prefixes like `find_`, `read_`, `compute_`, `process_`, `plot_` etc.) (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19) 
### New functions / parameters
- `eda_scr()`: Created own algorithm for SCR features extraction. (**since 0.1.92**) [#29](https://github.com/neuropsychology/NeuroKit.py/pull/29)
- Allow the user to skip some steps such as HRV or signal quality computation (**since 0.1.91**) [#28](https://github.com/neuropsychology/NeuroKit.py/pull/28)
- Added new QRS segmenter (pekkanen) method (**since 0.1.7**) [#22](https://github.com/neuropsychology/NeuroKit.py/pull/22)
### Major changes
- Enhanced HRV processing: computes HRV frequency domain power over time (**since 0.1.8**) [#24](https://github.com/neuropsychology/NeuroKit.py/pull/24)
### Minor changes
- Better separation between `ecg_preprocess` and `ecg_process` (and short vs long computation processes) (**since 0.1.7**) [#21](https://github.com/neuropsychology/NeuroKit.py/pull/21)
- Completely Separated bio_ecg and bio_ecg_preprocessing files (**since 0.1.7**) [#22](https://github.com/neuropsychology/NeuroKit.py/pull/22)
- Introducing CHANGELOG (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Added segmenter choice option for ecg processing (**since 0.1.6**) [#20](https://github.com/neuropsychology/NeuroKit.py/pull/20)
- Improved CONTRIBUTING.md (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Structural changes (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)
- Increase tests (**since 0.1.6**) [#19](https://github.com/neuropsychology/NeuroKit.py/pull/19)


