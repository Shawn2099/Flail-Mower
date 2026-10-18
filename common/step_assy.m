%% step_assy.m — combined assembly view from parsed solids (colored by solid)
clear; clc;
load('step_solids.mat','RES','PTS');
figure('Name','assembly');
hold on; grid on; axis equal;
cols = lines(size(RES,1));
for s = 1:size(RES,1)
    p = PTS{s};
    scatter3(p(:,1),p(:,2),p(:,3),12,repmat(cols(s,:),size(p,1),1),'filled');
    c = mean(p,1);
    text(c(1),c(2),c(3),sprintf('#%d',RES(s,1)),'FontSize',9,'FontWeight','bold');
end
xlabel('X mm'); ylabel('Y mm'); zlabel('Z mm');
title('medium.stp assembly (colors = solids). Which end is FRONT?');
view(-60,20);
saveas(gcf,'step_assy.png');
% inventory table, sorted by volume proxy (bbox)
fprintf('\ncell | size X x Y x Z mm | centroid\n');
for s = 1:size(RES,1)
    p = PTS{s}; c = mean(p,1);
    fprintf('#%-4d %6.0fx%6.0fx%6.0f @ (%.0f,%.0f,%.0f)\n', ...
        RES(s,1), RES(s,5)-RES(s,2), RES(s,6)-RES(s,3), RES(s,7)-RES(s,4), c(1),c(2),c(3));
end
fprintf('Wrote step_assy.png\n');
