%% step_measure.m — import medium.stp via PDE Toolbox, measure every solid (mm)
clear; clc;
model = createpde();
importGeometry(model, 'medium.stp');
g = model.Geometry;
fprintf('Cells(solids): %d  Faces: %d  Edges: %d  Vertices: %d\n', ...
    g.NumCells, g.NumFaces, g.NumEdges, g.NumVertices);
try
    V = volume(g);
    fprintf('volume() returned %d values, total %.0f mm^3\n', numel(V), sum(V));
catch ME
    fprintf('volume() failed: %s\n', ME.message);
    V = nan(g.NumCells,1);
end
generateMesh(model, 'Hmax', 15);
msh = model.Mesh;
fprintf('mesh nodes: %d elements: %d\n', size(msh.Nodes,2), size(msh.Elements,2));
fprintf('\ncell | x0 x1 | y0 y1 | z0 z1 (mm) | vol mm^3\n');
for c = 1:g.NumCells
    nid = findNodes(msh, 'region', 'Cell', c);
    p = msh.Nodes(:, nid);
    fprintf('%3d  %7.1f %7.1f  %7.1f %7.1f  %7.1f %7.1f   %.0f\n', c, ...
        min(p(1,:)), max(p(1,:)), min(p(2,:)), max(p(2,:)), min(p(3,:)), max(p(3,:)), V(min(c,numel(V))));
end
figure('Name','medium.stp'); pdegplot(model,'FaceLabels','off'); axis equal; grid on;
xlabel('X mm'); ylabel('Y mm'); zlabel('Z mm');
saveas(gcf, 'step_overview.png');
fprintf('Wrote step_overview.png\n');
