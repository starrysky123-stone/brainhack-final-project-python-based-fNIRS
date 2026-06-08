%% Export MATLAB/nirs-toolbox preprocessed HbO/HbR data for Python validation
%
% Purpose
% -------
% This script reruns the MATLAB/nirs-toolbox preprocessing steps and exports
% each participant's preprocessed HbO/HbR time series to CSV files. The Python
% validation script can then compare these CSV files against the MNE-Python FIF
% outputs in derivatives/preprocessed/.
%
% Run this script from MATLAB with nirs-toolbox on the MATLAB path.
% Do not upload the exported CSV files to GitHub.

clear

datadir = uigetdir([], 'Select the local fNIRS group directory');
if isequal(datadir, 0)
    error('No data directory selected.');
end

outdir = fullfile(pwd, 'validation', 'matlab_preprocessed');
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

raw = nirs.io.loadDirectory(datadir, {'Group', 'Subject'});

rename = nirs.modules.RenameStims();
rename.listOfChanges = {
    'stim_channel1', 'MA';
    'stim_channel2', 'PA';
    'stim_channel3', 'Control'};
raw = rename.run(raw);

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
fprintf('Datasets excluded because of incomplete MA/Control markers: %d\n', length(excl));
raw(excl) = [];

j_ss = nirs.modules.LabelShortSeperation();
raw = j_ss.run(raw);

resample = nirs.modules.Resample();
resample.Fs = 2;
downraw = resample.run(raw);

odconv = nirs.modules.OpticalDensity();
od = odconv.run(downraw);

mbll = nirs.modules.BeerLambertLaw();
hb = mbll.run(od);

trim = nirs.modules.TrimBaseline();
trim.preBaseline = 5;
trim.postBaseline = 5;
hb_trim = trim.run(hb);

manifest = table();

for i = 1:length(hb_trim)
    data_obj = hb_trim(i);
    subject = char(data_obj.demographics('Subject'));
    group = char(data_obj.demographics('Group'));

    if isempty(subject)
        subject = sprintf('subject_%03d', i);
    end
    if isempty(group)
        group = 'unknown';
    end

    subject_outdir = fullfile(outdir, group, subject);
    if ~exist(subject_outdir, 'dir')
        mkdir(subject_outdir);
    end

    link = data_obj.probe.link;
    channel_labels = strings(width(data_obj.data), 1);
    for ch = 1:height(link)
        channel_labels(ch) = sprintf('S%d_D%d_%s', link.source(ch), link.detector(ch), string(link.type(ch)));
    end

    data_table = array2table(data_obj.data, 'VariableNames', matlab.lang.makeValidName(channel_labels));
    data_table = addvars(data_table, data_obj.time, 'Before', 1, 'NewVariableNames', 'time');

    csv_path = fullfile(subject_outdir, sprintf('%s_matlab_hbo_hbr.csv', subject));
    writetable(data_table, csv_path);

    link_path = fullfile(subject_outdir, sprintf('%s_matlab_channel_link.csv', subject));
    writetable(link, link_path);

    manifest = [manifest; table(string(subject), string(group), string(csv_path), string(link_path), ...
        height(data_table), width(data_obj.data), ...
        'VariableNames', {'subject', 'group', 'csv_path', 'link_path', 'n_times', 'n_channels'})]; %#ok<AGROW>
end

manifest_path = fullfile(outdir, 'manifest.csv');
writetable(manifest, manifest_path);

fprintf('Exported MATLAB preprocessed data for %d subjects.\n', height(manifest));
fprintf('Manifest: %s\n', manifest_path);
