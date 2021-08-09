clear;close all
path = 'C:\Users\user\Desktop\python采集数据集\0809\走动zht';

cd(path)
for ii= 0:48
    name = (['out',num2str(ii),'.fc32'])
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
    
    save(['Data',num2str(ii),'ComplexC1.mat'],['data',num2str(1)])
    save(['Data',num2str(ii),'ComplexC2.mat'],['data',num2str(2)])

%     for i = 12%1:20%num_mear
%     %     figure
% %          plot(real(data1(i,:)),'-*')
%          hold on
%          plot(real(data2(i,:)))
%          pause(0.01)
%     end
    
%     figure
%     title('实部')
%     figure
    imagesc([real(data2(:,:))])
    saveas(gca,[path,'\fig\fig',num2str(ii),'.tif'])
    
end

% figure
% for i = 1:num_mear
%     result(i,:) = xcorr(data1(i,:),(data2(i,:)));
%     plot(abs(result(i,:)))
%     hold on
% end
% title('相关性幅度')