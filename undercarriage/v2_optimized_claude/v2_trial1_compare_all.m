% V2_TRIAL1_COMPARE_ALL  Four traction-drive options vs real estate scenarios (282 kg, 180x72x37 tracks).
% Writes trial1_compare.png.  Base MATLAB.  Tags: params marked [EST] are unverified (see TRIAL1_DRIVE.md).
%   A Mecwin 1.2kW BLDC, 9T, generic 30A ctrl       (metal gears, proven)
%   B Robokits 1418ZXF 500W, 8T, 1.5x current cap   (nylon gears)
%   C BM1418ZXF 750W, 8T, 1.5x current cap          (nylon gears)
%   D LION EV 1kW rickshaw motor + locked 1:10 diff + 12T pinion, 55A ctrl (steel gears)
%   E LION EV 1000W paddle-rickshaw kit: no torque/rpm/ratio published -> NOT GRADABLE
clear; clc; close all;
g=9.81; Rp=0.10526; Ls=1.0013; gauge=0.52; Wm=0.18; Z=48; M=282; W=M*g; A=2*Ls*Wm; Fmow=100;
soil=struct('n',{0.7,0.5},'kc',{5.27,13.19},'kp',{1515.04,692.15},'f',{0.04,0.08});   % dry, wet
opt=struct('nm',{'A Mecwin 1.2kW','B 1418ZXF 500W','C BM1418ZXF 750W','D LION 13.5A+diff 10T'}, ...
 'G',{Z/9, Z/8, Z/8, 48}, ...        % chain+gearbox after the rated-output shaft (1418ZXF 1:6 is inside the motor)
 'eta',{0.95, 0.95, 0.95, 0.95*0.9}, ...% chain (x gearbox for D)
 'Tr',{25, 10, 15.36, 1.75}, ...         % rated motor-output torque Nm
 'Tcap',{25, 15, 23, 3.3}, ...          % allowed peak (A nameplate; B,C 1.5x nylon cap; D 2x [EST])
 'n',{275, 450, 480, 3000}, ...         % rated output rpm
 'em',{0.85, 0.72, 0.72, 0.85}, ...     % motor+gear efficiency [EST: nylon hub 0.72]
 'cost',{16321,12320,12370,14800}, 'clo',{14321,10320,10370,14000},'chi',{18321,14320,14370,15800});
% scenarios: name, soil, slope, pivot mu (0 none), speed m/s
S={'Flat dry mow',1,0,0,0.5; 'Flat wet mow',2,0,0,0.5; '5deg dry',1,5,0,0.5; '8deg wet',2,8,0,0.5; ...
   'Pivot dry mu.5',1,0,0.5,0.3; 'Pivot wet mu.6',2,0,0.6,0.3};
ns=size(S,1); no=numel(opt); Tw=zeros(ns,1); Tm=zeros(ns,no); use=Tm; Pel=Tm;
for i=1:ns
  s=soil(S{i,2}); th=S{i,3}; mu=S{i,4}; v=S{i,5};
  keq=s.kc/Wm+s.kp; p=W*cosd(th)/A*1e-3; z=(p/keq)^(1/s.n); Rc=2*Wm*Ls*keq*z^(s.n+1)/(s.n+1)*1e3;
  Tw(i)=((W*sind(th)+Rc+s.f*W*cosd(th)+Fmow)/2)*Rp + mu*W*Ls/4/gauge*Rp;
  for j=1:no
    Tm(i,j)=Tw(i)/(opt(j).G*opt(j).eta); use(i,j)=Tm(i,j)/opt(j).Tr;
    side=2; Pel(i,j)=side*Tw(i)*(v/Rp)/(opt(j).em*0.95*0.95);   % both sides electrical W
  end
end
cols=[0.12 0.35 0.65; 0.85 0.45 0.1; 0.8 0.2 0.2; 0.2 0.6 0.3];
f=figure('Visible','off','Position',[50 50 1500 1000],'Color','w');
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');
% 1 utilisation
nexttile; b=bar(use*100); for j=1:no, b(j).FaceColor=cols(j,:); end; hold on
yline(100,'k-','rated','LabelHorizontalAlignment','left');
for j=1:no, plot([0.5 ns+.5],100*opt(j).Tcap/opt(j).Tr*[1 1]+2*j,':','Color',cols(j,:),'LineWidth',1.5); end
set(gca,'XTickLabel',S(:,1),'XTickLabelRotation',25); ylabel('motor torque, % of rated'); title('Torque demand vs rated (dotted = each option''s allowed peak)');
legend({opt.nm},'Location','northwest'); grid on; ylim([0 220])
% 2 torque-speed envelope at wheel
nexttile; hold on; vv=linspace(0.05,1.0,200); w=vv/Rp*60/(2*pi);
for j=1:no
  Twcap=opt(j).Tcap*opt(j).G*opt(j).eta; wb=opt(j).n/opt(j).G;        % base wheel rpm
  Pmax=Twcap*wb*2*pi/60; ww=vv/Rp; T=min(Twcap,Pmax./ww); T(w>wb*1.15)=NaN;
  plot(vv,T,'-','Color',cols(j,:),'LineWidth',2);
end
for i=1:ns, yline(Tw(i),':',S{i,1},'LabelHorizontalAlignment','right','FontSize',7); end
xlabel('ground speed m/s'); ylabel('wheel torque per side, Nm'); title('What each drive can deliver (solid) vs what the ground asks (dotted)');
legend({opt.nm},'Location','northeast'); grid on; ylim([0 240]);
% 3 cost
nexttile; c=[opt.cost]*2/1000; lo=[opt.clo]*2/1000; hi=[opt.chi]*2/1000; bb=bar(c); bb.FaceColor='flat'; bb.CData=cols; hold on
errorbar(1:no,c,c-lo,hi-c,'k.','LineWidth',1.5); set(gca,'XTickLabel',{opt.nm},'XTickLabelRotation',15);
ylabel('both sides, Rs thousand'); title('Cost (motor+controller+gearbox+pinion+bracket+shroud)'); grid on
for j=1:no, text(j,hi(j)+0.8,sprintf('%.1fk',c(j)),'HorizontalAlignment','center'); end
% 4 energy
nexttile; cyc=[100 8]; Pcyc=(Pel(1,:)*cyc(1)+Pel(5,:)*cyc(2))/sum(cyc); Wh=Pcyc;  % W avg = Wh per hour
bar(Pcyc); b4=bar(Pcyc); b4.FaceColor='flat'; b4.CData=cols; hold on
for j=1:no, text(j,Pcyc(j)+8,sprintf('%.0f W',Pcyc(j)),'HorizontalAlignment','center'); end
set(gca,'XTickLabel',{opt.nm},'XTickLabelRotation',15); ylabel('avg traction power, W (=Wh per hour)');
title('Row cycle: 100 s mow @0.5 m/s + 8 s pivot, dry'); grid on
saveas(f,fullfile(fileparts(mfilename('fullpath')),'trial1_compare.png'));
fprintf('Wheel Nm/side: '); for i=1:ns, fprintf('%s %.0f | ',S{i,1},Tw(i)); end; fprintf('\n\n');
fprintf('%-22s','util %rated'); fprintf('%-18s',opt.nm); fprintf('\n');
for i=1:ns, fprintf('%-22s',S{i,1}); fprintf('%-18.0f',use(i,:)*100); fprintf('\n'); end
fprintf('\ntop speed m/s: '); for j=1:no, fprintf('%s %.2f | ',opt(j).nm,opt(j).n/opt(j).G*2*pi*Rp/60); end
fprintf('\npeak margin (pivot wet mu.6), cap/need: '); for j=1:no, fprintf('%s %.2f | ',opt(j).nm,opt(j).Tcap/Tm(6,j)); end
fprintf('\navg traction W in row cycle: '); fprintf('%.0f ',Pcyc); fprintf('\n');
fprintf('pivot wet bus current both sides @46V: '); fprintf('%.0f A ',Pel(6,:)/46); fprintf('\n');
