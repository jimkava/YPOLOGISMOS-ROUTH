classdef ControlSystemsAnalyzer < matlab.apps.AppBase
% ControlSystemsAnalyzer  — Αναλυτής Συστημάτων Αυτόματου Ελέγχου
%
% Απαιτεί: MATLAB R2019b+ με Control System Toolbox
%
% Χρήση:  >> ControlSystemsAnalyzer

    %% ── UI Component Properties ────────────────────────────────────────────
    properties (Access = public)
        UIFigure            matlab.ui.Figure

        % Top bar
        TopPanel            matlab.ui.container.Panel
        AppTitleLabel       matlab.ui.control.Label
        SubTitleLabel       matlab.ui.control.Label
        CalculateButton     matlab.ui.control.Button

        % Main grid
        MainGrid            matlab.ui.container.GridLayout

        % Left panel
        LeftPanel           matlab.ui.container.Panel
        LeftGrid            matlab.ui.container.GridLayout

        % Gc inputs
        GcGroupBox          matlab.ui.container.Panel
        GcNumEditField      matlab.ui.control.EditField
        GcDenEditField      matlab.ui.control.EditField

        % G inputs
        GGroupBox           matlab.ui.container.Panel
        GNumEditField       matlab.ui.control.EditField
        GDenEditField       matlab.ui.control.EditField

        % H inputs
        HGroupBox           matlab.ui.container.Panel
        HNumEditField       matlab.ui.control.EditField
        HDenEditField       matlab.ui.control.EditField

        % Settings
        SettingsGroupBox    matlab.ui.container.Panel
        FeedbackButtonGroup matlab.ui.container.ButtonGroup
        NegFeedbackButton   matlab.ui.control.RadioButton
        PosFeedbackButton   matlab.ui.control.RadioButton
        KMaxEditField       matlab.ui.control.EditField
        KStepsEditField     matlab.ui.control.EditField
        WMinEditField       matlab.ui.control.EditField
        WMaxEditField       matlab.ui.control.EditField

        % Right panel & tabs
        RightPanel          matlab.ui.container.Panel
        ResultsTabGroup     matlab.ui.container.TabGroup
        BlockDiagramTab     matlab.ui.container.Tab
        TFResultsTab        matlab.ui.container.Tab
        RouthTab            matlab.ui.container.Tab
        PolesTab            matlab.ui.container.Tab
        RLocusTab           matlab.ui.container.Tab
        BodeTab             matlab.ui.container.Tab
        NicholsTab          matlab.ui.container.Tab

        % Block diagram
        BlockAxes           matlab.ui.control.UIAxes

        % TF Results
        TFOpenLoopText      matlab.ui.control.TextArea
        TFClosedLoopText    matlab.ui.control.TextArea
        TFCharEqText        matlab.ui.control.TextArea

        % Routh
        RouthTableUI        matlab.ui.control.Table
        StabilityLabel      matlab.ui.control.Label
        CharEqNoteLabel     matlab.ui.control.Label

        % Poles / Zeros
        PolesTableUI        matlab.ui.control.Table

        % Root Locus
        RLocusAxes          matlab.ui.control.UIAxes

        % Bode
        BodeMagAxes         matlab.ui.control.UIAxes
        BodePhaseAxes       matlab.ui.control.UIAxes
        MarginsLabel        matlab.ui.control.Label

        % Nichols
        NicholsAxes         matlab.ui.control.UIAxes
    end

    %% ── Private Calculation Methods ────────────────────────────────────────
    methods (Access = private)

        % ── Polynomial Utilities ──────────────────────────────────────────

        function c = parseCoeffs(~, str)
            str = strtrim(str);
            if isempty(str), c = 1; return; end
            c = str2num(str); %#ok<ST2NM>
            if isempty(c), c = 1; end
        end

        function str = poly2str_local(~, coeffs)
            p = coeffs(:)';
            while length(p) > 1 && abs(p(1)) < 1e-12
                p = p(2:end);
            end
            n = length(p) - 1;
            if n < 0, str = '0'; return; end
            str = ''; first = true;
            for i = 1:length(p)
                pow = n - i + 1;
                c   = p(i);
                if abs(c) < 1e-9, continue; end
                ca  = abs(c);
                if ~first
                    str = [str, ternary(c < 0, ' - ', ' + ')]; %#ok<AGROW>
                elseif c < 0
                    str = [str, '-']; %#ok<AGROW>
                end
                showC = ~(abs(ca - 1) < 1e-9 && pow > 0);
                if showC
                    str = [str, formatNum(ca)]; %#ok<AGROW>
                end
                if pow == 1,     str = [str, 's']; %#ok<AGROW>
                elseif pow > 1,  str = [str, 's^', num2str(pow)]; %#ok<AGROW>
                end
                first = false;
            end
            if isempty(str), str = '0'; end

            function s = ternary(cond, a, b)
                if cond, s = a; else, s = b; end
            end
            function s = formatNum(x)
                if x == round(x), s = num2str(x, '%g');
                else,              s = num2str(x, '%.4f'); end
            end
        end

        % ── Routh–Hurwitz ─────────────────────────────────────────────────

        function [routhMat, nOrder] = buildRouth(~, coeffs)
            p = coeffs(:)';
            while length(p) > 1 && abs(p(1)) < 1e-12, p = p(2:end); end
            nOrder = length(p) - 1;
            if nOrder <= 0, routhMat = p(1); return; end
            cols = ceil((nOrder + 1) / 2);
            routhMat = zeros(nOrder + 1, cols);
            for i = 1:2:nOrder+1, routhMat(1, ceil(i/2)) = p(i); end
            if nOrder >= 1
                for i = 2:2:nOrder+1, routhMat(2, ceil(i/2)) = p(i); end
            end
            for row = 3:nOrder+1
                pivot = routhMat(row-1, 1);
                if abs(pivot) < 1e-9
                    pivot = 1e-6;
                    routhMat(row-1, 1) = pivot;
                end
                for j = 1:cols-1
                    routhMat(row, j) = ...
                        (routhMat(row-1,1)*routhMat(row-2,j+1) - ...
                         routhMat(row-2,1)*routhMat(row-1,j+1)) / routhMat(row-1,1);
                end
            end
        end

        % ── Block Diagram ─────────────────────────────────────────────────

        function renderBlockDiagram(app, gcn, gcd_v, gn, gd, hn, hd, fbNeg)
            ax = app.BlockAxes;
            cla(ax);
            hold(ax, 'on');
            ax.XLim = [0 10]; ax.YLim = [0 6];
            ax.Color = [0.02 0.04 0.08];
            ax.XAxis.Visible = 'off'; ax.YAxis.Visible = 'off';
            ax.Box = 'off';

            wireC  = [0   0.78 1.00];
            boxC   = [0.05 0.10 0.19];
            boxEdC = [0.16 0.27 0.44];
            fbC    = [0.70 0.56 1.00];
            labC   = [0.94 0.65 0.00];
            sigC   = [0   0.78 0.88];
            fontN  = 'Courier New';

            midY = 3.8; fbY = 1.6;

            showH = ~(length(hn)==1 && abs(hn(1)-1)<1e-9 && ...
                      length(hd)==1 && abs(hd(1)-1)<1e-9);

            % --- Wires ---
            plot(ax,[0.3 1.5],[midY midY],'Color',wireC,'LineWidth',2);
            plot(ax,[1.9 2.5],[midY midY],'Color',wireC,'LineWidth',2);
            plot(ax,[4.1 4.8],[midY midY],'Color',wireC,'LineWidth',2);
            plot(ax,[6.4 7.5],[midY midY],'Color',wireC,'LineWidth',2);
            plot(ax,[7.5 9.7],[midY midY],'Color',wireC,'LineWidth',2);

            % --- Labels R, Y ---
            text(ax,0.25,midY,'R(s)','Color',wireC,'HorizontalAlignment','right',...
                'FontSize',11,'FontName',fontN,'VerticalAlignment','middle');
            text(ax,9.75,midY,'Y(s)','Color',wireC,'HorizontalAlignment','left',...
                'FontSize',11,'FontName',fontN,'VerticalAlignment','middle');

            % --- Summing junction ---
            th = linspace(0,2*pi,60);
            R = 0.22; sx = 1.70;
            fill(ax, sx+R*cos(th), midY+R*sin(th), boxC, 'EdgeColor', boxEdC, 'LineWidth',1.5);
            plot(ax,[sx-0.13 sx+0.13],[midY midY],'Color',wireC,'LineWidth',1.5);
            plot(ax,[sx sx],[midY-0.13 midY+0.13],'Color',wireC,'LineWidth',1.5);
            text(ax,sx-0.07,midY+0.08,'+','Color',wireC,'FontSize',9,'FontName',fontN);
            fbSign = char(8722); % − minus
            if ~fbNeg, fbSign = '+'; end
            text(ax,sx-0.20,midY-0.06,fbSign,'Color',fbC,'FontSize',12,'FontName',fontN);

            % E(s)
            text(ax,2.20,midY+0.28,'E(s)','Color',labC,'HorizontalAlignment','center',...
                'FontSize',9,'FontName',fontN);

            % --- Gc box ---
            rectangle(ax,'Position',[2.5 midY-0.55 1.6 1.1],...
                'FaceColor',boxC,'EdgeColor',boxEdC,'LineWidth',1.5,'Curvature',0.1);
            text(ax,3.30,midY+0.28,'Ελεγκτής','Color',labC,'HorizontalAlignment','center',...
                'FontSize',9,'FontName',fontN);
            text(ax,3.30,midY-0.08,'Gc(s)','Color',sigC,'HorizontalAlignment','center',...
                'FontSize',12,'FontName',fontN,'FontWeight','bold');

            % U(s)
            text(ax,4.45,midY+0.28,'U(s)','Color',labC,'HorizontalAlignment','center',...
                'FontSize',9,'FontName',fontN);

            % --- G box ---
            rectangle(ax,'Position',[4.8 midY-0.55 1.6 1.1],...
                'FaceColor',boxC,'EdgeColor',boxEdC,'LineWidth',1.5,'Curvature',0.1);
            text(ax,5.60,midY+0.28,'Διεργασία','Color',labC,'HorizontalAlignment','center',...
                'FontSize',9,'FontName',fontN);
            text(ax,5.60,midY-0.08,'G(s)','Color',sigC,'HorizontalAlignment','center',...
                'FontSize',12,'FontName',fontN,'FontWeight','bold');

            % Output junction dot
            plot(ax,7.50,midY,'o','Color',wireC,'MarkerFaceColor',wireC,'MarkerSize',6);

            % --- Feedback path down ---
            plot(ax,[7.50 7.50],[midY fbY],'Color',fbC,'LineWidth',2);

            if showH
                plot(ax,[1.70 7.50],[fbY fbY],'Color',fbC,'LineWidth',2);
                rectangle(ax,'Position',[4.20 fbY-0.45 1.6 0.9],...
                    'FaceColor',boxC,'EdgeColor',fbC,'LineWidth',1.5,'Curvature',0.1);
                text(ax,5.00,fbY+0.17,'Αισθητήρας','Color',labC,'HorizontalAlignment','center',...
                    'FontSize',9,'FontName',fontN);
                text(ax,5.00,fbY-0.12,'H(s)','Color',fbC,'HorizontalAlignment','center',...
                    'FontSize',12,'FontName',fontN,'FontWeight','bold');
                plot(ax,[1.70 1.70],[fbY midY-0.22],'Color',fbC,'LineWidth',2);
            else
                plot(ax,[1.70 7.50],[fbY fbY],'Color',fbC,'LineWidth',2);
                plot(ax,[1.70 1.70],[fbY midY-0.22],'Color',fbC,'LineWidth',2);
                text(ax,4.60,fbY+0.22,'Μοναδιαία Ανάδραση  H(s) = 1',...
                    'Color',fbC,'HorizontalAlignment','center','FontSize',9,'FontName',fontN);
            end

            % Transfer function strings as annotations
            gcStr = [app.poly2str_local(gcn) ' / (' app.poly2str_local(gcd_v) ')'];
            gStr  = [app.poly2str_local(gn)  ' / (' app.poly2str_local(gd)   ')'];
            text(ax,3.30,midY-0.38,gcStr,'Color',[0.53 0.6 0.72],...
                'HorizontalAlignment','center','FontSize',8,'FontName',fontN,...
                'Interpreter','none');
            text(ax,5.60,midY-0.38,gStr,'Color',[0.53 0.6 0.72],...
                'HorizontalAlignment','center','FontSize',8,'FontName',fontN,...
                'Interpreter','none');
            if showH
                hStr = [app.poly2str_local(hn) ' / (' app.poly2str_local(hd) ')'];
                text(ax,5.00,fbY-0.38,hStr,'Color',[0.53 0.6 0.72],...
                    'HorizontalAlignment','center','FontSize',8,'FontName',fontN,...
                    'Interpreter','none');
            end

            hold(ax,'off');
        end

        % ── TF Results ────────────────────────────────────────────────────

        function renderTFResults(app, OL, CL, charPoly)
            [olN, olD] = tfdata(OL,'v');
            [clN, clD] = tfdata(CL,'v');
            sep = repmat('─',1,40);
            app.TFOpenLoopText.Value = {
                app.poly2str_local(olN), sep, app.poly2str_local(olD)};
            app.TFClosedLoopText.Value = {
                app.poly2str_local(clN), sep, app.poly2str_local(clD)};
            app.TFCharEqText.Value = {[app.poly2str_local(charPoly), '  =  0']};
        end

        % ── Routh Rendering ───────────────────────────────────────────────

        function renderRouth(app, charPoly)
            [rMat, nOrd] = app.buildRouth(charPoly);
            rows = size(rMat,1);
            cols = size(rMat,2);

            colNames = cell(1, cols+1);
            colNames{1} = 'Γραμμή';
            for j = 1:cols, colNames{j+1} = ['Στ. ' num2str(j)]; end

            data = cell(rows, cols+1);
            for i = 1:rows
                data{i,1} = ['s^' num2str(nOrd-i+1)];
                for j = 1:cols
                    v = rMat(i,j);
                    if abs(v) < 1e-9, data{i,j+1} = '0';
                    elseif v == round(v), data{i,j+1} = num2str(v,'%g');
                    else, data{i,j+1} = num2str(v,'%.4f'); end
                end
            end

            app.RouthTableUI.ColumnName = colNames;
            app.RouthTableUI.Data = data;

            firstCol = rMat(:,1);
            changes = 0;
            for i = 2:length(firstCol)
                if firstCol(i-1)*firstCol(i) < 0, changes = changes + 1; end
            end

            hasZero = any(abs(firstCol) < 1e-5);

            if hasZero
                app.StabilityLabel.Text = ...
                    ['⚠ ΟΡΙΑΚΗ ΕΥΣΤΑΘΕΙΑ / Πόλοι στον jω-άξονα' newline ...
                     '  Μηδενικός πρώτος όρος στον πίνακα Routh'];
                app.StabilityLabel.FontColor = [0.94 0.65 0];
            elseif changes == 0
                app.StabilityLabel.Text = ...
                    '✓  ΕΥΣΤΑΘΕΣ — Όλοι οι πόλοι στο αριστερό ημιεπίπεδο (ΑΗΕ)';
                app.StabilityLabel.FontColor = [0 0.91 0.48];
            else
                app.StabilityLabel.Text = sprintf( ...
                    '✗  ΑΣΤΑΘΕΣ — %d αλλαγ(ές) πρόσημου  →  %d πόλ(οι) στο ΔΗΕ', ...
                    changes, changes);
                app.StabilityLabel.FontColor = [1 0.27 0.27];
            end

            app.CharEqNoteLabel.Text = ...
                ['Χαρακτηριστική εξίσωση:  ' app.poly2str_local(charPoly) '  =  0'];
        end

        % ── Poles / Zeros ─────────────────────────────────────────────────

        function renderPoles(app, CL, OL)
            clP = pole(CL); clZ = zero(CL);
            olP = pole(OL); olZ = zero(OL);

            all_v = [clP(:); clZ(:); olP(:); olZ(:)];
            types = [ repmat({'ΚΒ Πόλος'},   numel(clP),1);
                      repmat({'ΚΒ Μηδενικό'},numel(clZ),1);
                      repmat({'ΑΒ Πόλος'},   numel(olP),1);
                      repmat({'ΑΒ Μηδενικό'},numel(olZ),1) ];

            data = cell(numel(all_v), 6);
            for i = 1:numel(all_v)
                re = real(all_v(i)); im = imag(all_v(i));
                if re > 1e-6,              loc = 'ΔΗΕ (Ασταθής)';
                elseif abs(re)<1e-5 && abs(im)>1e-6, loc = 'jω-άξονας';
                else,                      loc = 'ΑΗΕ (Ευσταθής)'; end
                data{i,1} = types{i};
                data{i,2} = num2str(re,  '%.4f');
                data{i,3} = num2str(im,  '%.4f');
                data{i,4} = num2str(abs(all_v(i)), '%.4f');
                data{i,5} = num2str(angle(all_v(i))*180/pi, '%.1f');
                data{i,6} = loc;
            end

            app.PolesTableUI.ColumnName = {'Τύπος','Re','Im','|ρ|','θ (°)','Θέση'};
            app.PolesTableUI.Data = data;
        end

        % ── Root Locus ────────────────────────────────────────────────────

        function renderRootLocus(app, OL, kMax, kSteps)
            ax = app.RLocusAxes;
            cla(ax); hold(ax,'on');
            ax.Color = [0.027 0.063 0.118];
            ax.XColor = [0.53 0.60 0.72]; ax.YColor = [0.53 0.60 0.72];
            ax.GridColor = [0.05 0.11 0.19];
            ax.FontName = 'Courier New'; ax.FontSize = 11;
            grid(ax,'on');

            [olN, olD] = tfdata(OL,'v');
            nPoles = length(olD) - 1;
            if nPoles <= 0
                text(ax,0,0,'Δεν υπάρχουν πόλοι ανοικτού βρόχου.',...
                    'Color',[0.53 0.6 0.72],'HorizontalAlignment','center',...
                    'FontName','Courier New');
                hold(ax,'off'); return;
            end

            K = linspace(0, kMax, kSteps+1);
            colors_c = {[0 0.78 0.88],[0.94 0.65 0],[0 0.91 0.48],...
                        [0.71 0.56 1],[1 0.40 0.53],[1 0.55 0.26]};

            loci = cell(nPoles,1);
            for li = 1:nPoles, loci{li} = struct('re',[],'im',[]); end

            prevR = [];
            for ki = 1:length(K)
                Kv = K(ki);
                % char poly = olD + K*olN (zero-padded to same length)
                padN = [zeros(1, length(olD)-length(olN)), olN];
                cp   = olD + Kv * padN;
                r    = roots(cp); r = r(:);
                if length(r) < nPoles
                    r = [r; zeros(nPoles-length(r),1)];
                end
                r = r(1:nPoles);
                if isempty(prevR)
                    [~,idx] = sort(angle(r)); r = r(idx);
                else
                    used = false(nPoles,1);
                    ordered = zeros(nPoles,1) + 1i*zeros(nPoles,1);
                    for ii = 1:nPoles
                        d = abs(r - prevR(ii)); d(used) = Inf;
                        [~,bj] = min(d);
                        ordered(ii) = r(bj); used(bj) = true;
                    end
                    r = ordered;
                end
                prevR = r;
                for li = 1:nPoles
                    loci{li}.re(end+1) = real(r(li));
                    loci{li}.im(end+1) = imag(r(li));
                end
            end

            % Collect range for axis scaling
            allRe = []; allIm = [];
            for li = 1:nPoles
                allRe = [allRe, loci{li}.re]; %#ok<AGROW>
                allIm = [allIm, loci{li}.im]; %#ok<AGROW>
            end

            for li = 1:nPoles
                col = colors_c{mod(li-1,numel(colors_c))+1};
                % Split at large jumps
                re_v = loci{li}.re; im_v = loci{li}.im;
                dx = diff(re_v); dy = diff(im_v);
                jumps = find(sqrt(dx.^2+dy.^2) > 3);
                segs = [1, jumps+1; [jumps, length(re_v)]];
                for si = 1:size(segs,2)
                    s1 = segs(1,si); s2 = segs(2,si);
                    if s2-s1 < 1, continue; end
                    plot(ax, re_v(s1:s2), im_v(s1:s2), ...
                        'Color', col, 'LineWidth', 2.5, ...
                        'DisplayName', ifelse(si==1, ['Λόκος ' num2str(li)], '_'));
                end
            end

            % OL poles ×
            olPoles = pole(OL);
            plot(ax,real(olPoles),imag(olPoles),'x',...
                'Color',[1 0.27 0.27],'MarkerSize',14,'LineWidth',3,...
                'DisplayName','Πόλοι Α.Β. × (K=0)');

            % OL zeros ○
            olZeros = zero(OL);
            if ~isempty(olZeros)
                plot(ax,real(olZeros),imag(olZeros),'o',...
                    'Color',[0 0.91 0.48],'MarkerSize',12,'LineWidth',3,...
                    'DisplayName','Μηδενικά Α.Β. ○ (K→∞)');
            end

            % Axes & RHP shading
            reMin = min(allRe); reMax = max(allRe);
            imAbs = max(abs(allIm));
            rePad = max((reMax-reMin)*0.15, 1);
            imPad = max(imAbs*0.15, 1);
            xRange = [reMin-rePad, reMax+rePad];
            yRange = [-(imAbs+imPad), imAbs+imPad];
            ax.XLim = xRange; ax.YLim = yRange;

            plot(ax,[0 0],yRange,'Color',[1 0.3 0.3 0.5],...
                'LineWidth',1.5,'LineStyle',':','HandleVisibility','off');
            plot(ax,xRange,[0 0],'Color',[0.4 0.55 0.7 0.35],...
                'LineWidth',1,'HandleVisibility','off');
            patch(ax,[0 xRange(2) xRange(2) 0],...
                 [yRange(1) yRange(1) yRange(2) yRange(2)],...
                 [1 0.27 0.27],'FaceAlpha',0.05,'EdgeColor','none',...
                 'HandleVisibility','off');

            xlabel(ax,'Re(s)','Color',[0.78 0.85 0.94],'FontSize',13);
            ylabel(ax,'Im(s)','Color',[0.78 0.85 0.94],'FontSize',13);
            title(ax,['Γεωμετρικός Τόπος Ριζών — K \in [0, ' num2str(kMax) ']'],...
                'Color',[0.78 0.85 0.94],'FontSize',13,'FontName','Courier New');
            leg = legend(ax,'show');
            leg.TextColor = [0.78 0.85 0.94];
            leg.Color     = [0.05 0.09 0.13];
            leg.EdgeColor = [0.12 0.19 0.31];
            hold(ax,'off');

            function v = ifelse(cond,a,b)
                if cond, v=a; else, v=b; end
            end
        end

        % ── Bode ──────────────────────────────────────────────────────────

        function renderBode(app, OL, wMin, wMax)
            omega = logspace(wMin, wMax, 600);
            [mag, phase, ~] = bode(OL, omega);
            mag   = squeeze(mag);
            phase = squeeze(phase);
            magdB = 20*log10(mag + 1e-300);
            phaseUnwrap = unwrap(phase*pi/180)*180/pi;

            ax1 = app.BodeMagAxes; cla(ax1); hold(ax1,'on');
            ax1.Color = [0.027 0.063 0.118];
            ax1.XColor = [0.53 0.60 0.72]; ax1.YColor = [0.53 0.60 0.72];
            ax1.GridColor = [0.05 0.11 0.19];
            ax1.XScale = 'log'; ax1.FontName = 'Courier New'; ax1.FontSize=11;
            grid(ax1,'on');
            plot(ax1,omega,magdB,'Color',[0 0.78 0.88],'LineWidth',2.5);
            plot(ax1,[omega(1) omega(end)],[0 0],'--','Color',[1 0.27 0.27],...
                'LineWidth',1,'HandleVisibility','off');
            ylabel(ax1,'Πλάτος (dB)','Color',[0.78 0.85 0.94],'FontSize',12);
            title(ax1,'Διάγραμμα Bode','Color',[0.78 0.85 0.94],...
                'FontSize',13,'FontName','Courier New');
            hold(ax1,'off');

            ax2 = app.BodePhaseAxes; cla(ax2); hold(ax2,'on');
            ax2.Color = [0.027 0.063 0.118];
            ax2.XColor = [0.53 0.60 0.72]; ax2.YColor = [0.53 0.60 0.72];
            ax2.GridColor = [0.05 0.11 0.19];
            ax2.XScale = 'log'; ax2.FontName = 'Courier New'; ax2.FontSize=11;
            grid(ax2,'on');
            plot(ax2,omega,phaseUnwrap,'Color',[0.94 0.65 0],'LineWidth',2.5);
            plot(ax2,[omega(1) omega(end)],[-180 -180],'--',...
                'Color',[1 0.27 0.27],'LineWidth',1,'HandleVisibility','off');
            xlabel(ax2,'ω (rad/s)','Color',[0.78 0.85 0.94],'FontSize',12);
            ylabel(ax2,'Φάση (°)','Color',[0.78 0.85 0.94],'FontSize',12);
            hold(ax2,'off');

            try
                [gm, pm, wgm, wpm] = margin(OL);
                gmDB = 20*log10(max(gm,1e-12));
                gmTxt = sprintf('%.2f dB @ ω=%.3f rad/s', gmDB, wgm);
                pmTxt = sprintf('%.2f°   @ ω=%.3f rad/s', pm,   wpm);
                app.MarginsLabel.Text = ...
                    ['G.M.: ' gmTxt '   |   P.M.: ' pmTxt];
                if gmDB > 6 && pm > 45
                    app.MarginsLabel.FontColor = [0 0.91 0.48];
                elseif gmDB > 0 && pm > 0
                    app.MarginsLabel.FontColor = [0.94 0.65 0];
                else
                    app.MarginsLabel.FontColor = [1 0.27 0.27];
                end
            catch
                app.MarginsLabel.Text = 'Αδύνατος υπολογισμός περιθωρίων.';
                app.MarginsLabel.FontColor = [0.53 0.60 0.72];
            end
        end

        % ── Nichols ───────────────────────────────────────────────────────

        function renderNichols(app, OL, wMin, wMax)
            omega = logspace(wMin, wMax, 600);
            [mag, phase, ~] = bode(OL, omega);
            mag   = squeeze(mag);
            phase = squeeze(phase);
            magdB = 20*log10(mag + 1e-300);
            phaseUnwrap = unwrap(phase*pi/180)*180/pi;

            ax = app.NicholsAxes; cla(ax); hold(ax,'on');
            ax.Color = [0.027 0.063 0.118];
            ax.XColor = [0.53 0.60 0.72]; ax.YColor = [0.53 0.60 0.72];
            ax.GridColor = [0.05 0.11 0.19];
            ax.FontName = 'Courier New'; ax.FontSize = 11;
            grid(ax,'on');

            plot(ax,phaseUnwrap,magdB,'Color',[0 0.78 0.88],'LineWidth',2.5,...
                'DisplayName','G(j\omega)');

            % Critical point
            plot(ax,-180,0,'x','Color',[1 0.27 0.27],'MarkerSize',14,...
                'LineWidth',3,'DisplayName','Κρίσιμο (−180°, 0 dB)');

            % Reference lines
            xLim = ax.XLim;
            yLim = ax.YLim;
            plot(ax,xLim,[0 0],'Color',[0.16 0.23 0.36],'LineWidth',0.5,...
                'LineStyle',':','HandleVisibility','off');
            plot(ax,[-180 -180],yLim,'Color',[1 0.27 0.27 0.4],'LineWidth',1,...
                'LineStyle',':','HandleVisibility','off');

            xlabel(ax,'Φάση (°)','Color',[0.78 0.85 0.94],'FontSize',12);
            ylabel(ax,'Πλάτος (dB)','Color',[0.78 0.85 0.94],'FontSize',12);
            title(ax,'Διάγραμμα Nichols','Color',[0.78 0.85 0.94],...
                'FontSize',13,'FontName','Courier New');
            leg = legend(ax,'show');
            leg.TextColor = [0.78 0.85 0.94];
            leg.Color     = [0.05 0.09 0.13];
            leg.EdgeColor = [0.12 0.19 0.31];
            hold(ax,'off');
        end

        % ── Component Factories ───────────────────────────────────────────

        function panel = makeTFPanel(app, parent, row, titleStr)
            panel = uipanel(parent);
            panel.Title = titleStr;
            panel.BackgroundColor = [0.05 0.09 0.13];
            panel.BorderColor     = [0.16 0.27 0.44];
            panel.ForegroundColor = [0.94 0.65 0.00];
            panel.FontSize  = 11; panel.FontWeight = 'bold';
            panel.Layout.Row = row; panel.Layout.Column = 1;
        end

        function [numEF, denEF] = addTFFields(~, panel, defNum, defDen)
            g = uigridlayout(panel);
            g.ColumnWidth = {90,'1x'}; g.RowHeight = {26,26};
            g.BackgroundColor = [0.05 0.09 0.13];
            g.Padding = [6 6 6 6]; g.RowSpacing = 4; g.ColumnSpacing = 6;

            nLbl = uilabel(g,'Text','Αριθμητής:');
            nLbl.FontColor = [0.53 0.60 0.72]; nLbl.FontSize = 10;
            nLbl.Layout.Row = 1; nLbl.Layout.Column = 1;

            numEF = uieditfield(g,'text','Value',defNum);
            numEF.BackgroundColor = [0.02 0.05 0.10];
            numEF.FontColor = [0 0.78 0.88];
            numEF.FontName = 'Courier New'; numEF.FontSize = 12;
            numEF.Layout.Row = 1; numEF.Layout.Column = 2;

            dLbl = uilabel(g,'Text','Παρονομαστής:');
            dLbl.FontColor = [0.53 0.60 0.72]; dLbl.FontSize = 10;
            dLbl.Layout.Row = 2; dLbl.Layout.Column = 1;

            denEF = uieditfield(g,'text','Value',defDen);
            denEF.BackgroundColor = [0.02 0.05 0.10];
            denEF.FontColor = [0 0.78 0.88];
            denEF.FontName = 'Courier New'; denEF.FontSize = 12;
            denEF.Layout.Row = 2; denEF.Layout.Column = 2;
        end

        % ── Main createComponents ─────────────────────────────────────────

        function createComponents(app)
            BG  = [0.027 0.043 0.078];
            SRF = [0.050 0.090 0.130];

            %% Figure
            app.UIFigure = uifigure('Visible','off');
            app.UIFigure.Color = BG;
            app.UIFigure.Position = [50 50 1280 820];
            app.UIFigure.Name = 'Αναλυτής Συστημάτων Αυτόματου Ελέγχου';
            app.UIFigure.Resize = 'on';

            %% Top bar
            app.TopPanel = uipanel(app.UIFigure);
            app.TopPanel.BackgroundColor = [0.02 0.04 0.08];
            app.TopPanel.BorderType = 'none';
            app.TopPanel.Position = [0 780 1280 40];

            app.AppTitleLabel = uilabel(app.TopPanel,...
                'Text','⚙  ΑΝΑΛΥΤΗΣ ΣΥΣΤΗΜΑΤΩΝ ΑΥΤΟΜΑΤΟΥ ΕΛΕΓΧΟΥ');
            app.AppTitleLabel.FontColor  = [0 0.78 0.88];
            app.AppTitleLabel.FontSize   = 13;
            app.AppTitleLabel.FontWeight = 'bold';
            app.AppTitleLabel.FontName   = 'Courier New';
            app.AppTitleLabel.Position   = [12 10 700 22];

            app.SubTitleLabel = uilabel(app.TopPanel,...
                'Text','IEC / IEEE Control Systems Toolbox');
            app.SubTitleLabel.FontColor = [0.23 0.33 0.50];
            app.SubTitleLabel.FontSize  = 9;
            app.SubTitleLabel.FontName  = 'Courier New';
            app.SubTitleLabel.Position  = [12 1 400 12];

            app.CalculateButton = uibutton(app.TopPanel,'push',...
                'Text','▶  ΥΠΟΛΟΓΙΣΜΟΣ');
            app.CalculateButton.Position        = [1120 7 148 26];
            app.CalculateButton.BackgroundColor = [0.94 0.65 0];
            app.CalculateButton.FontColor       = [0 0 0];
            app.CalculateButton.FontWeight      = 'bold';
            app.CalculateButton.FontSize        = 11;
            app.CalculateButton.ButtonPushedFcn = ...
                createCallbackFcn(app,@CalcButtonPushed,true);

            %% Main grid (below top bar)
            app.MainGrid = uigridlayout(app.UIFigure);
            app.MainGrid.ColumnWidth  = {430,'1x'};
            app.MainGrid.RowHeight    = {'1x'};
            app.MainGrid.BackgroundColor = BG;
            app.MainGrid.Padding      = [6 6 6 6];
            app.MainGrid.ColumnSpacing = 8;
            app.MainGrid.Position     = [0 0 1280 778];

            %% Left panel
            app.LeftPanel = uipanel(app.MainGrid);
            app.LeftPanel.BackgroundColor = BG;
            app.LeftPanel.BorderType = 'none';
            app.LeftPanel.Layout.Row = 1; app.LeftPanel.Layout.Column = 1;

            app.LeftGrid = uigridlayout(app.LeftPanel);
            app.LeftGrid.ColumnWidth = {'1x'};
            app.LeftGrid.RowHeight   = {110,110,110,200};
            app.LeftGrid.BackgroundColor = BG;
            app.LeftGrid.Padding     = [0 0 0 0];
            app.LeftGrid.RowSpacing  = 6;

            % Gc
            app.GcGroupBox = app.makeTFPanel(app.LeftGrid, 1, 'Ελεγκτής — Gc(s)');
            [app.GcNumEditField, app.GcDenEditField] = ...
                app.addTFFields(app.GcGroupBox, '1', '1 1');

            % G
            app.GGroupBox = app.makeTFPanel(app.LeftGrid, 2, 'Διεργασία — G(s)');
            [app.GNumEditField, app.GDenEditField] = ...
                app.addTFFields(app.GGroupBox, '1', '1 2 1');

            % H
            app.HGroupBox = app.makeTFPanel(app.LeftGrid, 3, 'Ανάδραση — H(s)  [1/1 = μοναδιαία]');
            [app.HNumEditField, app.HDenEditField] = ...
                app.addTFFields(app.HGroupBox, '1', '1');

            % Settings
            app.SettingsGroupBox = uipanel(app.LeftGrid);
            app.SettingsGroupBox.Title = 'Ρυθμίσεις';
            app.SettingsGroupBox.BackgroundColor = SRF;
            app.SettingsGroupBox.BorderColor     = [0.16 0.27 0.44];
            app.SettingsGroupBox.ForegroundColor = [0.94 0.65 0];
            app.SettingsGroupBox.FontSize        = 11;
            app.SettingsGroupBox.FontWeight      = 'bold';
            app.SettingsGroupBox.Layout.Row      = 4;
            app.SettingsGroupBox.Layout.Column   = 1;

            sg = uigridlayout(app.SettingsGroupBox);
            sg.ColumnWidth = {110,'1x',80,'1x'};
            sg.RowHeight   = {30,26,26,26};
            sg.BackgroundColor = SRF;
            sg.Padding = [6 6 6 6]; sg.RowSpacing=5; sg.ColumnSpacing=6;

            % Feedback type
            app.FeedbackButtonGroup = uibuttongroup(sg);
            app.FeedbackButtonGroup.BackgroundColor = SRF;
            app.FeedbackButtonGroup.BorderType = 'none';
            app.FeedbackButtonGroup.Layout.Row    = 1;
            app.FeedbackButtonGroup.Layout.Column = [1 4];

            app.NegFeedbackButton = uiradiobutton(app.FeedbackButtonGroup,...
                'Text','Αρνητική Ανάδραση (−)','Value',true,...
                'FontColor',[0.78 0.85 0.94],'FontSize',11);
            app.NegFeedbackButton.Position = [4 5 200 22];

            app.PosFeedbackButton = uiradiobutton(app.FeedbackButtonGroup,...
                'Text','Θετική Ανάδραση (+)','Value',false,...
                'FontColor',[0.78 0.85 0.94],'FontSize',11);
            app.PosFeedbackButton.Position = [210 5 180 22];

            % Row 2: K max, K steps
            l1=uilabel(sg,'Text','K max (Γ.Τ.Ρ.):');
            l1.FontColor=[0.53 0.60 0.72];l1.FontSize=10;
            l1.Layout.Row=2;l1.Layout.Column=1;
            app.KMaxEditField = uieditfield(sg,'text','Value','100');
            app.KMaxEditField.BackgroundColor=[0.02 0.05 0.10];
            app.KMaxEditField.FontColor=[0 0.78 0.88];
            app.KMaxEditField.FontName='Courier New';app.KMaxEditField.FontSize=11;
            app.KMaxEditField.Layout.Row=2;app.KMaxEditField.Layout.Column=2;

            l2=uilabel(sg,'Text','K βήματα:');
            l2.FontColor=[0.53 0.60 0.72];l2.FontSize=10;
            l2.Layout.Row=2;l2.Layout.Column=3;
            app.KStepsEditField = uieditfield(sg,'text','Value','200');
            app.KStepsEditField.BackgroundColor=[0.02 0.05 0.10];
            app.KStepsEditField.FontColor=[0 0.78 0.88];
            app.KStepsEditField.FontName='Courier New';app.KStepsEditField.FontSize=11;
            app.KStepsEditField.Layout.Row=2;app.KStepsEditField.Layout.Column=4;

            % Row 3: w min, w max
            l3=uilabel(sg,'Text','Bode ω (10^n) από:');
            l3.FontColor=[0.53 0.60 0.72];l3.FontSize=10;
            l3.Layout.Row=3;l3.Layout.Column=1;
            app.WMinEditField = uieditfield(sg,'text','Value','-2');
            app.WMinEditField.BackgroundColor=[0.02 0.05 0.10];
            app.WMinEditField.FontColor=[0 0.78 0.88];
            app.WMinEditField.FontName='Courier New';app.WMinEditField.FontSize=11;
            app.WMinEditField.Layout.Row=3;app.WMinEditField.Layout.Column=2;

            l4=uilabel(sg,'Text','έως (10^n):');
            l4.FontColor=[0.53 0.60 0.72];l4.FontSize=10;
            l4.Layout.Row=3;l4.Layout.Column=3;
            app.WMaxEditField = uieditfield(sg,'text','Value','3');
            app.WMaxEditField.BackgroundColor=[0.02 0.05 0.10];
            app.WMaxEditField.FontColor=[0 0.78 0.88];
            app.WMaxEditField.FontName='Courier New';app.WMaxEditField.FontSize=11;
            app.WMaxEditField.Layout.Row=3;app.WMaxEditField.Layout.Column=4;

            % Row 4: note
            note=uilabel(sg,'Text',...
                'Εισάγετε συντελεστές από υψηλότερη σε χαμηλότερη δύναμη, χωρισμένοι με κενό. π.χ. "1 3 2" → s²+3s+2');
            note.FontColor=[0.35 0.45 0.60];note.FontSize=9;
            note.WordWrap='on';
            note.Layout.Row=4;note.Layout.Column=[1 4];

            %% Right panel
            app.RightPanel = uipanel(app.MainGrid);
            app.RightPanel.BackgroundColor = SRF;
            app.RightPanel.BorderColor     = [0.12 0.19 0.31];
            app.RightPanel.Layout.Row = 1; app.RightPanel.Layout.Column = 2;

            app.ResultsTabGroup = uitabgroup(app.RightPanel);
            app.ResultsTabGroup.Position = [4 4 820 762];

            %% ─ Tab: Block Diagram ─
            app.BlockDiagramTab = uitab(app.ResultsTabGroup,'Title','Δομικό Διάγραμμα');
            app.BlockDiagramTab.BackgroundColor = BG;
            app.BlockAxes = uiaxes(app.BlockDiagramTab);
            app.BlockAxes.Position = [10 10 800 730];
            app.BlockAxes.Color    = [0.02 0.04 0.08];
            app.BlockAxes.XAxis.Visible = 'off';
            app.BlockAxes.YAxis.Visible = 'off';
            app.BlockAxes.Box = 'off';

            %% ─ Tab: TF Results ─
            app.TFResultsTab = uitab(app.ResultsTabGroup,'Title','Σ.Μ. Αποτελέσματα');
            app.TFResultsTab.BackgroundColor = BG;
            tfg = uigridlayout(app.TFResultsTab);
            tfg.ColumnWidth = {'1x'}; tfg.RowHeight = {24,160,24,160,24,80};
            tfg.BackgroundColor = BG; tfg.Padding = [10 10 10 10];

            function lbl = makeLabel(parent,row,txt)
                lbl = uilabel(parent,'Text',txt);
                lbl.FontColor=[0.94 0.65 0];lbl.FontSize=12;lbl.FontWeight='bold';
                lbl.Layout.Row=row;lbl.Layout.Column=1;
            end
            function ta = makeTA(parent,row,defVal)
                ta = uitextarea(parent,'Value',{defVal});
                ta.FontName='Courier New';ta.FontSize=13;
                ta.FontColor=[0 0.91 0.48];
                ta.BackgroundColor=[0.02 0.05 0.10];
                ta.Layout.Row=row;ta.Layout.Column=1;
            end
            makeLabel(tfg,1,'Ανοικτός Βρόχος — Gc(s)·G(s)·H(s)');
            app.TFOpenLoopText   = makeTA(tfg,2,'Αναμονή υπολογισμού...');
            makeLabel(tfg,3,'Κλειστός Βρόχος — T(s)');
            app.TFClosedLoopText = makeTA(tfg,4,'Αναμονή υπολογισμού...');
            app.TFClosedLoopText.FontColor = [0 0.78 0.88];
            makeLabel(tfg,5,'Χαρακτηριστική Εξίσωση');
            app.TFCharEqText = makeTA(tfg,6,'Αναμονή υπολογισμού...');
            app.TFCharEqText.FontColor = [0.94 0.65 0];

            %% ─ Tab: Routh–Hurwitz ─
            app.RouthTab = uitab(app.ResultsTabGroup,'Title','Routh–Hurwitz');
            app.RouthTab.BackgroundColor = BG;
            rg = uigridlayout(app.RouthTab);
            rg.ColumnWidth = {'1x'}; rg.RowHeight = {'1x',34,28};
            rg.BackgroundColor = BG; rg.Padding = [10 10 10 10];

            app.RouthTableUI = uitable(rg);
            app.RouthTableUI.Data = {'Αναμονή...'};
            app.RouthTableUI.BackgroundColor = [0.05 0.09 0.13; 0.07 0.12 0.20];
            app.RouthTableUI.ForegroundColor = [0 0.78 0.88];
            app.RouthTableUI.FontName = 'Courier New'; app.RouthTableUI.FontSize = 12;
            app.RouthTableUI.Layout.Row=1; app.RouthTableUI.Layout.Column=1;

            app.StabilityLabel = uilabel(rg,'Text','Αναμονή υπολογισμού...');
            app.StabilityLabel.FontColor  = [0.53 0.60 0.72];
            app.StabilityLabel.FontSize   = 14; app.StabilityLabel.FontWeight='bold';
            app.StabilityLabel.FontName   = 'Courier New';
            app.StabilityLabel.WordWrap   = 'on';
            app.StabilityLabel.Layout.Row=2; app.StabilityLabel.Layout.Column=1;

            app.CharEqNoteLabel = uilabel(rg,'Text','');
            app.CharEqNoteLabel.FontColor = [0.35 0.45 0.60];
            app.CharEqNoteLabel.FontSize  = 11;
            app.CharEqNoteLabel.FontName  = 'Courier New';
            app.CharEqNoteLabel.Layout.Row=3; app.CharEqNoteLabel.Layout.Column=1;

            %% ─ Tab: Poles / Zeros ─
            app.PolesTab = uitab(app.ResultsTabGroup,'Title','Πόλοι / Μηδενικά');
            app.PolesTab.BackgroundColor = BG;
            pg = uigridlayout(app.PolesTab);
            pg.ColumnWidth={'1x'}; pg.RowHeight={'1x'};
            pg.BackgroundColor=BG; pg.Padding=[10 10 10 10];

            app.PolesTableUI = uitable(pg);
            app.PolesTableUI.Data = {'Αναμονή...'};
            app.PolesTableUI.BackgroundColor = [0.05 0.09 0.13; 0.07 0.12 0.20];
            app.PolesTableUI.ForegroundColor = [0 0.78 0.88];
            app.PolesTableUI.FontName = 'Courier New'; app.PolesTableUI.FontSize=12;
            app.PolesTableUI.Layout.Row=1; app.PolesTableUI.Layout.Column=1;

            %% ─ Tab: Root Locus ─
            app.RLocusTab = uitab(app.ResultsTabGroup,'Title','Γ.Τ.Ρ.');
            app.RLocusTab.BackgroundColor = BG;
            app.RLocusAxes = uiaxes(app.RLocusTab);
            app.RLocusAxes.Position = [10 10 800 730];
            app.RLocusAxes.Color    = [0.027 0.063 0.118];
            app.RLocusAxes.XColor   = [0.53 0.60 0.72];
            app.RLocusAxes.YColor   = [0.53 0.60 0.72];
            app.RLocusAxes.GridColor= [0.05 0.11 0.19];
            app.RLocusAxes.FontName = 'Courier New';

            %% ─ Tab: Bode ─
            app.BodeTab = uitab(app.ResultsTabGroup,'Title','Bode');
            app.BodeTab.BackgroundColor = BG;
            bodeg = uigridlayout(app.BodeTab);
            bodeg.ColumnWidth={'1x'}; bodeg.RowHeight={28,'1x','1x'};
            bodeg.BackgroundColor=BG; bodeg.Padding=[8 8 8 8]; bodeg.RowSpacing=4;

            app.MarginsLabel = uilabel(bodeg,'Text','Αναμονή υπολογισμού...');
            app.MarginsLabel.FontColor=[0.78 0.85 0.94];app.MarginsLabel.FontSize=12;
            app.MarginsLabel.FontName='Courier New';
            app.MarginsLabel.Layout.Row=1;app.MarginsLabel.Layout.Column=1;

            app.BodeMagAxes = uiaxes(bodeg);
            app.BodeMagAxes.Layout.Row=2;app.BodeMagAxes.Layout.Column=1;
            app.BodeMagAxes.Color=[0.027 0.063 0.118];
            app.BodeMagAxes.XColor=[0.53 0.60 0.72];app.BodeMagAxes.YColor=[0.53 0.60 0.72];
            app.BodeMagAxes.GridColor=[0.05 0.11 0.19];app.BodeMagAxes.FontName='Courier New';

            app.BodePhaseAxes = uiaxes(bodeg);
            app.BodePhaseAxes.Layout.Row=3;app.BodePhaseAxes.Layout.Column=1;
            app.BodePhaseAxes.Color=[0.027 0.063 0.118];
            app.BodePhaseAxes.XColor=[0.53 0.60 0.72];app.BodePhaseAxes.YColor=[0.53 0.60 0.72];
            app.BodePhaseAxes.GridColor=[0.05 0.11 0.19];app.BodePhaseAxes.FontName='Courier New';

            %% ─ Tab: Nichols ─
            app.NicholsTab = uitab(app.ResultsTabGroup,'Title','Nichols');
            app.NicholsTab.BackgroundColor = BG;
            app.NicholsAxes = uiaxes(app.NicholsTab);
            app.NicholsAxes.Position = [10 10 800 730];
            app.NicholsAxes.Color    = [0.027 0.063 0.118];
            app.NicholsAxes.XColor   = [0.53 0.60 0.72];
            app.NicholsAxes.YColor   = [0.53 0.60 0.72];
            app.NicholsAxes.GridColor= [0.05 0.11 0.19];
            app.NicholsAxes.FontName = 'Courier New';

            app.UIFigure.Visible = 'on';
        end
    end

    %% ── Callbacks ──────────────────────────────────────────────────────────
    methods (Access = private)

        function CalcButtonPushed(app, ~)
            app.CalculateButton.Text   = '⏳  Υπολογισμός...';
            app.CalculateButton.Enable = 'off';
            drawnow;
            try
                gcn   = app.parseCoeffs(app.GcNumEditField.Value);
                gcd_v = app.parseCoeffs(app.GcDenEditField.Value);
                gn    = app.parseCoeffs(app.GNumEditField.Value);
                gd    = app.parseCoeffs(app.GDenEditField.Value);
                hn    = app.parseCoeffs(app.HNumEditField.Value);
                hd    = app.parseCoeffs(app.HDenEditField.Value);

                fbNeg  = app.NegFeedbackButton.Value;
                kMax   = str2double(app.KMaxEditField.Value);
                kSteps = str2double(app.KStepsEditField.Value);
                wMin   = str2double(app.WMinEditField.Value);
                wMax   = str2double(app.WMaxEditField.Value);

                if isnan(kMax),   kMax   = 100;  end
                if isnan(kSteps), kSteps = 200;  end
                if isnan(wMin),   wMin   = -2;   end
                if isnan(wMax),   wMax   =  3;   end
                if kMax   <= 0,   kMax   = 100;  end
                if kSteps <  10,  kSteps = 10;   end
                if wMin >= wMax,  wMin = wMax-2;  end

                Gc  = tf(gcn,  gcd_v);
                G   = tf(gn,   gd);
                H   = tf(hn,   hd);
                OL  = Gc * G * H;
                Fwd = Gc * G;

                if fbNeg
                    CL = feedback(Fwd, H, -1);
                else
                    CL = feedback(Fwd, H, +1);
                end

                [~, clDen] = tfdata(CL, 'v');
                charPoly   = clDen / clDen(1);

                app.renderBlockDiagram(gcn, gcd_v, gn, gd, hn, hd, fbNeg);
                app.renderTFResults(OL, CL, charPoly);
                app.renderRouth(charPoly);
                app.renderPoles(CL, OL);
                app.renderRootLocus(OL, kMax, kSteps);
                app.renderBode(OL, wMin, wMax);
                app.renderNichols(OL, wMin, wMax);

            catch err
                uialert(app.UIFigure, ...
                    ['Σφάλμα: ' err.message newline ...
                     'Ελέγξτε τους συντελεστές εισόδου.'], ...
                    'Σφάλμα Υπολογισμού', 'Icon','error');
            end
            app.CalculateButton.Text   = '▶  ΥΠΟΛΟΓΙΣΜΟΣ';
            app.CalculateButton.Enable = 'on';
        end
    end

    %% ── Public Constructor / Destructor ────────────────────────────────────
    methods (Access = public)

        function app = ControlSystemsAnalyzer()
            createComponents(app);
            registerApp(app, app.UIFigure);
            % Auto-calculate with default values on startup
            app.CalcButtonPushed([]);
            if nargout == 0
                clear app
            end
        end

        function delete(app)
            delete(app.UIFigure)
        end
    end
end
