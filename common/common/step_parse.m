%% step_parse.m — B-rep topology walk of medium.stp: per-solid bbox from edge vertices
function step_parse()
t0 = tic;
t = fileread('medium.stp');
lines = cellstr(splitlines(t));
emap = containers.Map('KeyType','int32','ValueType','int32');
for k = 1:numel(lines)
    ln = lines{k};
    if startsWith(ln,'#')
        id = sscanf(ln,'#%d=',1);
        if ~isempty(id), emap(int32(id)) = k; end
    end
end
fprintf('entities indexed: %d (%.1fs)\n', emap.Count, toc(t0));

solids = findEnt('MANIFOLD_SOLID_BREP');
fprintf('solids: %d\n', numel(solids));
RES = zeros(numel(solids),7);
PTS = cell(numel(solids),1);
for s = 1:numel(solids)
    pts = solidPts(solids(s));
    PTS{s} = pts;
    RES(s,:) = [solids(s), min(pts,[],1), max(pts,[],1)];
    fprintf('solid #%d  npts %d  X[%.1f %.1f] Y[%.1f %.1f] Z[%.1f %.1f]\n', ...
        solids(s), size(pts,1), RES(s,2),RES(s,5),RES(s,3),RES(s,6),RES(s,4),RES(s,7));
end
fprintf('UNION X[%.1f %.1f] Y[%.1f %.1f] Z[%.1f %.1f]\n', ...
    min(RES(:,2)),max(RES(:,3)),min(RES(:,4)),max(RES(:,5)),min(RES(:,6)),max(RES(:,7)));
save('step_solids.mat','RES','PTS','-v7.3');

figure('Name','solids');
n = numel(solids); nc = ceil(sqrt(n)); nr = ceil(n/nc);
for s = 1:n
    subplot(nr,nc,s); p = PTS{s};
    if size(p,1) > 4000, p = p(randperm(size(p,1),4000),:); end
    scatter3(p(:,1),p(:,2),p(:,3),2,'filled'); axis equal off;
    title(sprintf('#%d', RES(s,1)));
end
saveas(gcf,'step_solids.png');
fprintf('Wrote step_solids.png + step_solids.mat\n');

    function ids = findEnt(name)
        ids = [];
        kk = emap.keys;
        for m = 1:numel(kk)
            ln = lines{emap(kk{m})};
            if startsWith(ln, sprintf('#%d=%s', kk{m}, name)), ids(end+1) = kk{m}; end %#ok<AGROW>
        end
    end
    function r = refs(ln)
        tk = regexp(ln,'#(\d+)','tokens'); r = cellfun(@(c)str2double(c{1}),tk);
    end
    function nm = entName(id)
        if ~isKey(emap,int32(id)), nm = ''; return; end
        ln = lines{emap(int32(id))};
        m = regexp(ln,'^#\d+=([A-Z_0-9]+)','tokens','once');
        if isempty(m), nm = ''; else, nm = m{1}; end
    end
    function xyz = cartOf(id)
        ln = lines{emap(int32(id))};
        m = regexp(ln,'\(\s*([-+0-9.Ee]+)\s*,\s*([-+0-9.Ee]+)\s*,\s*([-+0-9.Ee]+)\s*\)','tokens','once');
        xyz = [str2double(m{1}) str2double(m{2}) str2double(m{3})];
    end
    function xyz = vertOf(id)
        r = refs(lines{emap(int32(id))});
        xyz = [0 0 0];
        for k = 1:numel(r)
            if strcmp(entName(r(k)),'CARTESIAN_POINT'), xyz = cartOf(r(k)); return; end
        end
    end
    function P = edgePts(id)
        r = refs(lines{emap(int32(id))}); P = zeros(0,3);
        for k = 1:numel(r)
            if strcmp(entName(r(k)),'VERTEX_POINT'), P = [P; vertOf(r(k))]; end %#ok<AGROW>
        end
    end
    function P = loopPts(id)
        ln = lines{emap(int32(id))}; P = zeros(0,3);
        if ~isempty(strfind(ln,'VERTEX_LOOP'))
            r = refs(ln);
            for k = 1:numel(r)
                if strcmp(entName(r(k)),'VERTEX_POINT'), P = [P; vertOf(r(k))]; end %#ok<AGROW>
            end
            return;
        end
        r = refs(ln);
        for k = 1:numel(r)
            nm = entName(r(k));
            if strcmp(nm,'ORIENTED_EDGE')
                rr = refs(lines{emap(int32(r(k)))});
                for q = 1:numel(rr)
                    if strcmp(entName(rr(q)),'EDGE_CURVE'), P = [P; edgePts(rr(q))]; end %#ok<AGROW>
                end
            elseif strcmp(nm,'EDGE_CURVE')
                P = [P; edgePts(r(k))]; %#ok<AGROW>
            end
        end
    end
    function P = facePts(id)
        r = refs(lines{emap(int32(id))}); P = zeros(0,3);
        for k = 1:numel(r)
            nm = entName(r(k));
            if strcmp(nm,'FACE_BOUND') || strcmp(nm,'FACE_OUTER_BOUND')
                rr = refs(lines{emap(int32(r(k)))});
                for q = 1:numel(rr)
                    nm2 = entName(rr(q));
                    if strcmp(nm2,'EDGE_LOOP') || strcmp(nm2,'VERTEX_LOOP'), P = [P; loopPts(rr(q))]; end %#ok<AGROW>
                end
            end
        end
    end
    function P = solidPts(id)
        r = refs(lines{emap(int32(id))}); P = zeros(0,3);
        for k = 1:numel(r)
            nm = entName(r(k));
            if strcmp(nm,'CLOSED_SHELL') || strcmp(nm,'OPEN_SHELL')
                rr = refs(lines{emap(int32(r(k)))});
                for q = 1:numel(rr)
                    if strcmp(entName(rr(q)),'ADVANCED_FACE'), P = [P; facePts(rr(q))]; end %#ok<AGROW>
                end
            end
        end
    end
end
