%% Export MATLAB/nirs-toolbox time-grid diagnostics by preprocessing stage
%
% Purpose
% -------
% This script exports non-signal time-grid summaries at multiple MATLAB
% preprocessing stages. It is designed to diagnose where MATLAB and MNE-Python
% time axes first diverge. The exported table contains no channel time series,
% only aggregate timing metadata per dataset and stage.
%
% Run this script from MATLAB with nirs-toolbox on the MATLAB path.

clear

script_path = mfilename('fullpath');
if isempty(script_path)
    project_root = pwd;
else
    project_root = fileparts(fileparts(script_path));
end

datadir = uigetdir([], 'Select the local fNIRS group directory');
if isequal(datadir, 0)
    error('No data directory selected.');
end

outdir = fullfile(project_root, 'validation');
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

diagnostics = table();

raw = nirs.io.loadDirectory(datadir, {'Group', 'Subject'});
diagnostics = append_time_grid_rows(diagnostics, raw, "raw_loaded");

rename = nirs.modules.RenameStims();
rename.listOfChanges = {
    'stim_channel1', 'MA';
    'stim_channel2', 'PA';
    'stim_channel3', 'Control'};
raw = rename.run(raw);
diagnostics = append_time_grid_rows(diagnostics, raw, "stim_renamed");

expectedConds = {'MA', 'Control'};
expectedN = 16;
excl = [];

for i = 1:length(raw)
    keys = raw(i).stimulus.keys;
    vals = raw(i).stimulus.values;

    for c = 1:length(expectedConds)
        cond = expectedConds{c};
        hit = find(strcmp(keys, cond), 1);

        if isempty(hit) || length(vals{hit}.onset) ~= expectedN
            excl(end + 1) = i; %#ok<SAGROW>
            break
        end
    end
end

excl = unique(excl);
raw(excl) = [];
diagnostics = append_time_grid_rows(diagnostics, raw, "event_filtered");

j_ss = nirs.modules.LabelShortSeperation();
raw = j_ss.run(raw);
diagnostics = append_time_grid_rows(diagnostics, raw, "short_separation_labeled");

resample = nirs.modules.Resample();
resample.Fs = 2;
downraw = resample.run(raw);
diagnostics = append_time_grid_rows(diagnostics, downraw, "resampled_2hz");

odconv = nirs.modules.OpticalDensity();
od = odconv.run(downraw);
diagnostics = append_time_grid_rows(diagnostics, od, "optical_density");

mbll = nirs.modules.BeerLambertLaw();
hb = mbll.run(od);
diagnostics = append_time_grid_rows(diagnostics, hb, "beer_lambert");

trim = nirs.modules.TrimBaseline();
trim.preBaseline = 5;
trim.postBaseline = 5;
hb_trim = trim.run(hb);
diagnostics = append_time_grid_rows(diagnostics, hb_trim, "trimmed");

diagnostics_path = fullfile(outdir, 'matlab_time_grid_by_stage.csv');
writetable(diagnostics, diagnostics_path);

fprintf('Exported MATLAB time-grid diagnostics for %d rows.\n', height(diagnostics));
fprintf('Diagnostics: %s\n', diagnostics_path);

function diagnostics = append_time_grid_rows(diagnostics, data_array, stage)
    for i = 1:length(data_array)
        data_obj = data_array(i);
        subject = char(data_obj.demographics('Subject'));
        group = char(data_obj.demographics('Group'));

        if isempty(subject)
            subject = sprintf('subject_%03d', i);
        end
        if isempty(group)
            group = 'unknown';
        end

        time = data_obj.time;
        if isempty(time)
            n_times = 0;
            t0 = NaN;
            t_end = NaN;
            median_dt = NaN;
            min_dt = NaN;
            max_dt = NaN;
        else
            n_times = length(time);
            t0 = time(1);
            t_end = time(end);
            dt = diff(time);
            if isempty(dt)
                median_dt = NaN;
                min_dt = NaN;
                max_dt = NaN;
            else
                median_dt = median(dt);
                min_dt = min(dt);
                max_dt = max(dt);
            end
        end

        diagnostics = [diagnostics; table( ...
            string(subject), string(group), string(stage), ...
            n_times, t0, t_end, median_dt, min_dt, max_dt, ...
            'VariableNames', {'subject', 'group', 'stage', 'n_times', ...
            't0', 't_end', 'median_dt', 'min_dt', 'max_dt'})]; %#ok<AGROW>
    end
end
