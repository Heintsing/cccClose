clear;close all
path = 'F:\zht\CCC\cccClose';
cd(path)

name = ('out.fc32');
fid=fopen(name,'rb');%打开文件
if(fid>0)
    [data,count]=fread(fid,'float32');
end
fclose(fid);%关闭文件
clear data_t fid


num_sample = 2000;
num_mear = count/num_sample/2;
for i = 1:num_mear
    data1(i,:) = data(1+num_sample*2*(i-1):2:num_sample-1+num_sample*2*(i-1))+1j*data(2+num_sample*2*(i-1):2:num_sample+num_sample*2*(i-1));
    data2(i,:) = data(1+num_sample+num_sample*2*(i-1):2:(-1)+num_sample*2*i)+1j*data(2+num_sample+num_sample*2*(i-1):2:num_sample*2*i);
end

figure
for i = 1:num_mear
     plot(real(data1(i,:)),'-*')
     hold on
     plot(real(data2(i,:)))
%     pause(2)
end
title('实部')