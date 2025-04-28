#include<stdio.h>
int main(){
	int n,i;
	printf("enter no.of processes");
	scanf("%d",&n);
	int at[n],bt[n],ct[n],tat[n],wt[n],rt[n];
	float avgt=0,avgw=0,avgr=0;
	for(i=0;i<n;i++){
		printf("enter %d process arrival time ",i+1);
		scanf("%d",&at[i]);
	}
	for(i=0;i<n;i++){
		printf("enter %d process burst time ",i+1);
		scanf("%d",&bt[i]);
	}
	printf("pno.\tAT\tBT\n");
	for(i=0;i<n;i++){
		printf("p%d\t%d\t%d\n",i+1,at[i],bt[i]);
	}
	ct[0]=bt[0];
	for(i=1;i<n;i++){
		ct[i]=ct[i-1]+bt[i];
	}
	for(i=0;i<n;i++){
		tat[i]=ct[i]-at[i];
		wt[i]=tat[i]-bt[i];
	}
	rt[0]=at[0];
	for(i=1;i<n;i++){
		rt[i]=ct[i-1];
	}
	for(i=0;i<n;i++){
		avgt+=tat[i];
		avgw+=wt[i];
		avgr+=rt[i];
	}
	printf("pno.\tAT\tBT\t CT\tTAT\tWT\tRT\n");
	for(i=0;i<n;i++){
		printf("p%d\t%d\t%d\t %d\t%d\t%d\t%d\n",i+1,at[i],bt[i],ct[i],tat[i],wt[i],rt[i]);
	}
	printf("\t\t\t\t%.2f\t%.2f\t%.2f\n",avgt/n,avgw/n,avgr/n);
	return 0;
}