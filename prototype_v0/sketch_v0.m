%% sketch_v0.m
% Rough 2-view sketch of prototype v0 (plan + elevation), compact/nimble size.
% Dimensions from sim_v0_frame.m. Base MATLAB only. Saves sketch_v0.png.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));

L_wb = 260; track = 420; D = 170; R = D/2; Ww = 45;   % NIMBLE
rail_x = 160; rt = 25;   % inboard of the wheels (wheel inner face at 187.5)
deck_w = track - 65; deck_l = L_wb + 90;   % deck sits BETWEEN the wheels
ink = [0.15 0.15 0.15]; blu = [0.25 0.35 0.85]; grn = [0.10 0.50 0.10]; red = [0.85 0.10 0.10];

f = figure('Color','w','Position',[80 20 1150 1300],'Name','prototype v0 - rough sketch');

%% ================= TOP VIEW =================
ax1 = subplot('Position',[0.06 0.55 0.88 0.40]); axes(ax1); hold on; axis equal off;
xlim([-400 480]); ylim([-360 420]);
plot([-400 480],[0 0],'Color',[0.92 0.92 0.92]);
plot([0 0],[-360 420],'Color',[0.92 0.92 0.92]);

rectangle('Position',[-deck_w/2 -deck_l/2 deck_w deck_l],'EdgeColor',blu,'LineWidth',1.3,'LineStyle','--');
rectangle('Position',[-125 -150 250 90],'FaceColor',[0.90 0.97 0.90],'EdgeColor',grn,'LineWidth',1.3);
for sx = [-1 1]
    rectangle('Position',[sx*rail_x-rt/2 -(L_wb/2-rt/2) rt L_wb-rt],'FaceColor',[0.80 0.80 0.85],'EdgeColor',ink,'LineWidth',1.1);
end
for sy = [-1 1]
    rectangle('Position',[-(rail_x+rt/2) sy*L_wb/2-rt/2 2*rail_x+rt rt],'FaceColor',[0.80 0.80 0.85],'EdgeColor',ink,'LineWidth',1.1);
end
th = linspace(0,2*pi,100);
plot(100*cos(th),100*sin(th),'--','Color',red,'LineWidth',1.6);
for sx = [-1 1]
    rectangle('Position',[sx*track/2-Ww/2  L_wb/2-D/2 Ww D],'Curvature',[0.55 1], ...
        'FaceColor',[0.90 0.90 0.90],'EdgeColor',ink,'LineWidth',1.1);
    rectangle('Position',[sx*track/2-Ww/2 -L_wb/2-D/2 Ww D],'Curvature',[0.55 1], ...
        'FaceColor',[0.55 0.55 0.62],'EdgeColor',ink,'LineWidth',1.1);
    plot([-track/2 track/2],[L_wb/2 L_wb/2],'Color',ink,'LineStyle',':');
    plot([-track/2 track/2],[-L_wb/2 -L_wb/2],'Color',ink,'LineStyle',':');
end

% dimensions
plot([-track/2 track/2],[330 330],'Color',ink,'LineWidth',0.8);
plot([-track/2 -track/2],[315 345],'Color',ink); plot([track/2 track/2],[315 345],'Color',ink);
text(0,355,'track 420','HorizontalAlignment','center','FontSize',9);
plot([410 410],[-L_wb/2 L_wb/2],'Color',ink,'LineWidth',0.8);
plot([395 425],[-L_wb/2 -L_wb/2],'Color',ink); plot([395 425],[L_wb/2 L_wb/2],'Color',ink);
text(440,0,'wheelbase 260','Rotation',90,'HorizontalAlignment','center','FontSize',9);
plot([-370 -370],[-deck_w/2 deck_w/2],'Color',blu,'LineWidth',0.8);
text(-388,0,'overall 465 W','Rotation',90,'FontSize',8,'Color',blu,'HorizontalAlignment','center');

% labels
text(0,290,'FRONT','HorizontalAlignment','center','FontWeight','bold');
text(0,-325,'REAR','HorizontalAlignment','center','FontWeight','bold');
text(track/2+60, L_wb/2,'2x idle','FontSize',9);
text(track/2+60,-L_wb/2,'2x hub','FontSize',9);
text(0,15,'cutter 200 swath','Color',red,'HorizontalAlignment','center','FontSize',9,'FontWeight','bold');
text(0,-105,'36V battery on deck','Color',grn,'HorizontalAlignment','center','FontSize',9);
text(140,205,'deck lid','Color',blu,'FontSize',9);
title('TOP VIEW (plan)   -   420 track / 260 wheelbase / ~465 x ~430 overall');

%% ================= SIDE VIEW =================
ax2 = subplot('Position',[0.06 0.07 0.88 0.40]); axes(ax2); hold on; axis equal off;
xlim([-360 420]); ylim([-45 620]);

plot([-330 400],[0 0],'k','LineWidth',1.6);
for x = [-L_wb/2 L_wb/2]
    rectangle('Position',[x-R 0 D D],'Curvature',[1 1],'FaceColor',[0.90 0.90 0.90],'EdgeColor',ink,'LineWidth',1.1);
end
rectangle('Position',[-172.5 85 345 25],'FaceColor',[0.80 0.80 0.85],'EdgeColor',ink,'LineWidth',1.1);
rectangle('Position',[-175 110 350 35],'FaceColor',[0.86 0.86 0.96],'EdgeColor',blu,'LineWidth',1.1);
rectangle('Position',[ -70 110 140 75],'FaceColor',[0.86 0.86 0.96],'EdgeColor',blu,'LineWidth',1.1,'LineStyle','--');
rectangle('Position',[-172 145 135 75],'FaceColor',[0.86 0.96 0.86],'EdgeColor',grn,'LineWidth',1.1);
text(-104,183,'battery','Color',grn,'HorizontalAlignment','center','FontSize',9);
rectangle('Position',[-22 62 44.5 66],'FaceColor',[0.60 0.60 0.68],'EdgeColor',ink,'LineWidth',1.1);
text(0,95,'775','Color','w','HorizontalAlignment','center','FontSize',9,'FontWeight','bold');
rectangle('Position',[-22 30 44 32],'FaceColor',[0.75 0.75 0.75],'EdgeColor',ink,'LineWidth',1);
plot([-100 100],[42 42],'Color',red,'LineWidth',3.5);
plot([-118 -118],[16 80],'Color',[0.45 0.45 0.45],'LineWidth',1.2);
plot([ 118  118],[16 80],'Color',[0.45 0.45 0.45],'LineWidth',1.2);
plot([-165 -305],[100 585],'Color',ink,'LineWidth',2.0);
plot([-305 -195],[585 585],'Color',ink,'LineWidth',2.0);
text(-250,605,'handle -> ~900','HorizontalAlignment','center','FontSize',9);

plot([190 190],[0 42],'Color',ink,'LineWidth',0.8);
plot([177 203],[0 0],'Color',ink); plot([177 203],[42 42],'Color',ink);
text(215,15,'cut height 25-60','FontSize',9);
plot([-215 215],[-30 -30],'Color',ink,'LineWidth',0.8);
plot([-215 -215],[-40 -20],'Color',ink); plot([215 215],[-40 -20],'Color',ink);
text(0,-42,'430 overall L','HorizontalAlignment','center','FontSize',8);
text(-350,205,'deck top ~145','FontSize',9,'Color',blu);
text(240,120,'25x25x1.6','FontSize',9);
text(240,100,'tube frame','FontSize',9);
text(250,300,'cutter spins at the centre - line tips clear the','FontSize',8);
text(250,278,'420-wide wheels by ~62 mm | deck (dashed) sits','FontSize',8);
text(250,256,'between the wheels; they stay exposed at the corners','FontSize',8);
title('SIDE VIEW (elevation)   -   4 wheels 170 OD, motor hangs centre, guard below');

out = fullfile(thisdir,'sketch_v0.png');
print(f,out,'-dpng','-r150');
fprintf('sketch saved: %s\n', out);
close(f);
