%% step_audit.m — list assembly tree + units of medium.stp (no import yet)
clear; clc;
t = fileread('medium.stp');
fprintf('chars: %d\n', numel(t));
pr = regexp(t, 'PRODUCT\(''[^'']+''', 'match');
fprintf('PRODUCT refs: %d\n', numel(pr));
names = {};
for k = 1:numel(pr)
    s = pr{k};
    q = strfind(s, '''');
    nm = s(q(1)+1:q(2)-1);
    names{end+1} = nm; %#ok<AGROW>
end
un = unique(names);
fprintf('--- unique product names (%d) ---\n', numel(un));
for k = 1:numel(un), fprintf('%s\n', un{k}); end
u = regexp(t, 'SI_UNIT\([^;]*\)', 'match');
for k = 1:numel(u), fprintf('UNIT: %s\n', u{k}); end
sch = regexp(t, 'FILE_SCHEMA\(\([^)]*\)\)', 'tokens', 'once');
if ~isempty(sch), fprintf('SCHEMA: %s\n', sch{1}); end
