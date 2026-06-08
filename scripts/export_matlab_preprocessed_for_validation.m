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

outdir = fullfile(project_root, 'validation', 'matlab_preprocessed');
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

raw = nirs.io.loadDirectory(datadir, {'Group', 'Subject'});
fprintf('Loaded datasets: %d\n', length(raw));

rename = nirs.modules.RenameStims();
rename.listOfChanges = {
    'stim_channel1', 'MA';
    'stim_channel2', 'PA';
    'stim_channel3', 'Control'};
raw = rename.run(raw);
fprintf('After stimulus rename: %d datasets\n', length(raw));

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
fprintf('After MA/Control marker filter: %d datasets\n', length(raw));

j_ss = nirs.modules.LabelShortSeperation();
raw = j_ss.run(raw);
fprintf('After short-separation labeling: %d datasets\n', length(raw));

resample = nirs.modules.Resample();
resample.Fs = 2;
downraw = resample.run(raw);
fprintf('After resampling: %d datasets\n', length(downraw));

odconv = nirs.modules.OpticalDensity();
od = odconv.run(downraw);
fprintf('After optical density conversion: %d datasets\n', length(od));

mbll = nirs.modules.BeerLambertLaw();
hb = mbll.run(od);
fprintf('After Beer-Lambert Law conversion: %d datasets\n', length(hb));

trim = nirs.modules.TrimBaseline();
trim.preBaseline = 5;
trim.postBaseline = 5;
hb_trim = trim.run(hb);
fprintf('After baseline trimming: %d datasets\n', length(hb_trim));

if isempty(hb_trim)
    error(['No datasets remained after MATLAB preprocessing. ', ...
        'Please confirm that the selected folder is the group root containing G1_3 and G4_6 subject folders.']);
end

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
