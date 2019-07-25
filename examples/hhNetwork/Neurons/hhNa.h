		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		>>    modules name: h		>>
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
h:		> 	Inactivation function (rate constant method)	>
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


>----------------------->--------------------------------------->
>	1		>	     ah				>
>			>	h= --------		     (1)>
>			>	    ah+bh			>
>			>					>
>----------------------->--------------------------------------->
>	2		>	dh/dt=ah x (1-h) - bh x h    (2)>
>	xxx.xx	>IV<	>					>
>----------------------->--------------------------------------->
	3		>	dh/dt=L[ah x (1-h) - bh x h] (3)>
      -1         >IV<	>					>
    3000     >1000 L<	>					>
>----------------------->--------------------------------------->



		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
ah:		> 	Rate parameter (1)				>	
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

>----------------------->----------------------------------------------->
>	1		>	         			(1)	>
>	xxx.xx	>A<	>	ah = A        				>
>----------------------->----------------------------------------------->
>	2		>		A (V+B)				>
>	xxx.xx	>A<	>	ah = --------------------	(2)	>
>	xxx.xx	>B<	>	          (C-V)/D 			>
>	xxx.xx	>C<	>	     1 + e        			>
>	xxx.xx	>D<	>						>
>			>						>
>----------------------->----------------------------------------------->
>	3		>		A (V+B)				>
>	0.07	>A<	>	ah = --------------------	(3)	>
>     -65.0	>B<	>	          (C-V)/D 			>
>		>C<	>	     1 - e        			>
>	xxx.xx	>D<	>						>
>			>						>
>----------------------->----------------------------------------------->
>	4		>	          (A-V)/B 		(4)	>
>	xxx.xx	>A<	>	ah = 1 + e        			>
>	xxx.xx	>B<	>						>
>			>						>
>----------------------->----------------------------------------------->
	5		>	         (B-V)/C 		(5)	>
	0.07   >.07 A<	>	ah = A e        			>
      -60.0    >-60 B<	>						>
	20.0	>20 C<	>						>
>----------------------->----------------------------------------------->
>	6		>		A 				>
>	xxx.xx	>A<	>	ah = --------------------	(6)	>
>	xxx.xx	>B<	>	          (B-V)/C 			>
>	xxx.xx	>C<	>	     1 + e        			>
>			>						>
>----------------------->----------------------------------------------->
>	7		>		A 				>
>	xxx.xx	>A<	>	ah = --------------------	(7)	>
>	xxx.xx	>B<	>	          (B-V)/C 			>
>	xxx.xx	>C<	>	     1 - e        			>
>			>						>
>----------------------->----------------------------------------------->
>	8		>		1 				>
>	xxx.xx	>A<	>	ah = --------------------	(8)	>
>	xxx.xx	>B<	>	          (A-V)/B 			>
>			>	     1 + e        			>
>			>						>
>----------------------->----------------------------------------------->
>	9		>		1 				>
>	xxx.xx	>A<	>	ah = --------------------	(9)	>
>	xxx.xx	>B<	>	          (A-V)/B 			>
>			>	     1 - e        			>
>			>						>
>----------------------->----------------------------------------------->

		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
bh:		> 	Rate parameter (2)				>	
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

>----------------------->----------------------------------------------->
>	1		>	         			(1)	>
>	xxx.xx	>A<	>	bh = A        				>
>----------------------->----------------------------------------------->
>	2		>		A (V+B)				>
>	xxx.xx	>A<	>	bh = --------------------	(2)	>
>	xxx.xx	>B<	>	          (C-V)/D 			>
>	xxx.xx	>C<	>	     1 + e        			>
>	xxx.xx	>D<	>						>
>			>						>
>----------------------->----------------------------------------------->
>	3		>		A (V+B)				>
>	xxx.xx	>A<	>	bh = --------------------	(3)	>
>	xxx.xx	>B<	>	          (C-V)/D 			>
>	xxx.xx	>C<	>	     1 - e        			>
>	xxx.xx	>D<	>						>
>			>						>
>----------------------->----------------------------------------------->
>	4		>	          (A-V)/B 		(4)	>
>	xxx.xx	>A<	>	bh = 1 + e        			>
>	xxx.xx	>B<	>						>
>			>						>
>----------------------->----------------------------------------------->
>	5		>	         (B-V)/C 		(5)	>
>	xxx.xx	>A<	>	bh = A e        			>
>	xxx.xx	>B<	>						>
>	xxx.xx	>C<	>						>
>----------------------->----------------------------------------------->
>	6		>		A 				>
>	xxx.xx	>A<	>	bh = --------------------	(6)	>
>	xxx.xx	>B<	>	          (B-V)/C 			>
>	xxx.xx	>C<	>	     1 + e        			>
>			>						>
>----------------------->----------------------------------------------->
>	7		>		A 				>
>	xxx.xx	>A<	>	bh = --------------------	(7)	>
>	xxx.xx	>B<	>	          (B-V)/C 			>
>	xxx.xx	>C<	>	     1 - e        			>
>			>						>
>----------------------->----------------------------------------------->
	8		>		1 				>
	-30.0  >-30 A<	>	bh = --------------------	(8)	>
	 10.0	>10 B<	>	          (A-V)/B 			>
			>	     1 + e        			>
			>						>
>----------------------->----------------------------------------------->
>	9		>		1 				>
>	xxx.xx	>A<	>	bh = --------------------	(9)	>
>	xxx.xx	>B<	>	          (A-V)/B 			>
>			>	     1 - e        			>
>			>						>
>----------------------->----------------------------------------------->

END:

