readChannelID1 = 702908;
readChannelID2 = 702909;

TemperatureFieldID = 1;
humidityFieldID = 2;
readAPIKey1 = 'EFOA7V3LPRZXDZEZ';
readAPIKey2 = 'XB5FQLAEIS6YJ0ZE';
[humidity1,time1] = thingSpeakRead(readChannelID1,'Fields',humidityFieldID,'NumMinutes',1200,'ReadKey',readAPIKey1);
[humidity2,time2] = thingSpeakRead(readChannelID2,'Fields',humidityFieldID,'NumMinutes',1200,'ReadKey',readAPIKey2);
temperarure1 = thingSpeakRead(readChannelID1,'Fields',TemperatureFieldID,'NumMinutes',1200,'ReadKey',readAPIKey1);
temperarure2 = thingSpeakRead(readChannelID2,'Fields',TemperatureFieldID,'NumMinutes',1200,'ReadKey',readAPIKey2);
humtot= zeros(size(humidity1,1)*2,1);
temptot= humtot;
for i=1:size(humidity1,1)
    timetot(2*i-1,1) =time1(i);
    timetot(2*i,1) =time2(i);
    humtot(2*i-1,1) = humidity1(i);
    humtot(2*i,1) = humidity2(i);
    temptot(2*i-1,1) = temperarure1(i);
    temptot(2*i,1) = temperarure2(i);
end 
tempmax= temptot;
tempmax(:,1) = 39.5;
tempmin= temptot;
tempmin(:,1) = 38;
hummax= humtot;
hummax(:,1) = 42.75;
hummin= humtot;
hummin(:,1) = 40.1;

avgHumidity = mean(humtot);
display(avgHumidity,'Average Humidity');
avgTemperature = mean(temptot);
display(avgHumidity,'Average Temperature');
plotyy(timetot,humtot,timetot, temptot);
title('Temperatura y Humedad')
hold on
plotyy(timetot,hummax,timetot, tempmax);
plotyy(timetot,hummin,timetot, tempmin);
figure()
plot(timetot,humtot);
hold on
plot(timetot,hummax, 'r');
plot(timetot,hummin, 'y');
title('Humedad')
figure()
plot(timetot,temptot);
hold on
plot(timetot,tempmax, 'r');
plot(timetot,tempmin, 'y');
title('Temperatura')

%%Activacion del control todo o nada para los calefactores
control = zeros(size(temptot,1),1);
for i=1:size(temptot,1)-1
    if temptot(i) < tempmax(i)
        if (temptot(i) < temptot(i+1))
            control(i+1) = 1;
        end
    end
    if temptot(i) > tempmax(i)
        control(i+1) = 0;
    end
    if temptot(i) < tempmin(i)
        control(i+1) = 1;
    end
end
figure()
plot(timetot,control, 'g');
title ('Activación todo o nada');
        
    


