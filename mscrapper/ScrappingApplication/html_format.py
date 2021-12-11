html_format_t = '''
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<!-- Meta setup -->
		<meta charset="UTF-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		<meta name="keywords" content="">
		<meta name="decription" content="">
		
		<!-- Title -->
		<title>Welcome</title>
		
		
		

		<!-- Include Bootstrap -->		
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">

			
		
		<style>
			/*
		========================
		Header area start
		========================
		*/

		    /*
		    font-family: 'Lekton', sans-serif;

    		font-family: 'Oswald', sans-serif;

    		*/


		@import url('https://fonts.googleapis.com/css2?family=Lekton:ital,wght@0,400;0,700;1,400&family=Oswald:wght@300;400;500;600;700&display=swap');


		body {{	
		    font-family: 'Lekton', sans-serif;		    
		    font-size: 16px;
		    font-weight: 400;    
			background: #FFFAF6;
			color: #404849;	
		}}

		a:hover {{
		    text-decoration: none;
		}}

		ul {{
		    list-style-type: none;
		    padding: 0;
		    margin: 0;
		}}

		::selection {{
		    color: white; 
		    background: #ff7675;
		}}

		::-webkit-selection {{
		    color: white; 
		    background: #ff7675;
		}}

		::-moz-selection {{
		    color: white; 
		    background: #ff7675;
		}}

		.scrolltotop {{
		    width: 40px;
		    height: 40px;
		    border-radius: 20px 20px 0 0;
		    background: rgba(0,0,0,.5);   
		    text-align: center;
		    padding-top: 8px;
		    font-size: 22px;
		    color: #ffffff;
		    position: fixed;
		    right: 5px;
		    bottom: 5px;
		    display: none;
		    transition: 0.2s all ease;
		    -webkit-transition: 0.2s all ease;
		    -moz-transition: 0.2s all ease;
		}}

		.scrolltotop:hover {{   
		    background: #000;
		    color: #fff;
		    box-shadow: 0px 0px 5px rgba(0,0,0,.5);
		    -webkit-box-shadow: 0px 0px 5px rgba(0,0,0,.5);
		    -moz-box-shadow: 0px 0px 5px rgba(0,0,0,.5);   
		}}

		/*copyright-area start*/

		.full-area {{
			margin-bottom: 15px;
		}}




		.copyright-area {{
		    padding: 40px 0 0px;    
		}}

		.copybdr {{
		    border-right: 1px solid #3F4748;
		}}

		.copy-left p {{
		    font-size: 24px;
		    color: #404849;
		    margin: 0;
		    padding-bottom: 10px;
		    

		}}

		.copy-right p {{
		    font-size: 24px;
		    color: #fa6a56;
		    margin: 0;
		    text-align: right;
		    font-weight: 500;
		    padding-bottom: 10px;
		    font-weight: bold;
		}}

		/*logo-area start*/

		.logobdr {{
		    border-right: 1px solid #3F4748;
		}}

		.logrgtp {{
		    position: relative;

		}}

		.logrgtp:after {{
		    content: "";
		    display: block;
		    position: absolute;
		    width: 1px;
		    height: 35px;
		    bottom: -10px;
		    left: 0;
		    background: #3F4748;   
		}}

		.logo-wrap {{    
		    border-top: 1px solid #3F4748;
		    border-bottom: 1px solid #3F4748;
		}}

		.logrgt {{    
		    border-top: 0px solid #3F4748;
		    border-bottom: 1px solid #3F4748;
		}}

		.logo-left {{
		    padding: 20px 0;
		}}

		.logo-left a img {{
		    width: 400px;
		}}

		.logrp1 h6 {{
		    font-family: 'Oswald', sans-serif;
		    font-size: 23px;
		    font-weight: bold;
		    margin: 0;
		    padding: 10px 10px 10px 10px; 
		    text-align: center;

		}}

		.logrp2 h6 {{
		    font-size: 23px;
		    margin: 0;
            padding: 3px 3px 3px 3px;
		    text-align: right;
		}}

		.logsp span {{
		    width: 100%;
		    height: 2px;
		    background: #3F4748;
		    display: block;
		    margin-top: 5px;
		}}

		.logo-right {{
		    position: relative;
		   
		}}



		.logrp3 h4 {{
		    font-family: 'Oswald', sans-serif;
		    font-size: 35px;
		    color: #E96F5B;
		    font-weight: bold;    
		    text-align: right;
		    margin: 0;
		    padding-top: 50px;
		    letter-spacing: 11px;
		    
		    
		    
		}}

		/*summer-area start*/
		.summer-area {{
		    padding: 30px 0 20px;
		}}

		.sum-part1 h6 {{
		    font-size: 22px;
		    border-bottom: 1px solid #3F4748;
		    margin-bottom: 15px;
		    padding-bottom: 5px;
		}}

		.sum-part1 .sumbdr2 {{
		    border-left: 1px solid #3F4748;
		    border-right: 1px solid #3F4748;
		    padding: 0 10px;

		}}

		.sum-part1 h6 .sum-ctn {{
		    font-family: 'Oswald', sans-serif;
		    font-size: 45px;
		    font-weight: 500;
		    margin-right: 15px;

		}}

		.sum-part1 ul li {{
		    display: inline-block;
		    padding: 5px 0;

		}}

		.sum-part1 .sumpt1 {{
		    font-size: 24px;
		    margin-right: 15px;
		}}

		.sum-part1 .sumpt2 {{
		    font-size: 24px;
		    background: #3F4748;
		    color: #F96A56;
		    padding: 0 15px;
		    
		    font-weight: 600;
		}}

		.sum-part1 img {{
		    width: 25px;
		    margin-right: 10px;    
		}}

		.sum-part1 p {{
		    font-size: 24px;
		    margin-bottom: 10px;
		}}

		.sum-part1 .sumbulctn {{
		    border-bottom: 1px solid #3F4748;
		}}

		.sum-part2 ul {{
		    border-bottom: 1px solid #3F4748;
		}}

		.sum-part2 ul li {{
		    border-right: 1px solid #3F4748;
		    margin-right: 5px;
		    display: inline-block;
		    padding-right: 20px;
		    font-size: 24px;
		}}

		.sum-part2 ul li:last-child {{
		    border-right: none;
		}}

		.sum-part1 .sumplus {{
		    margin-left: 80px;
		}}

		.sum-part2 {{
		    padding: 5px 0 0;
		}}

		.sum-part3 {{
		    padding: 10px 0;
		}}

		.sum-part3 ul li {{
		    font-size: 24px;
		    padding: 15px 0 0;
		    border-bottom: 1px solid #3F4748;   
		    display: flex;
		    justify-content: space-between;    
		}}

		.sum-part3 ul li span {{
		    border-right: 1px solid #3F4748;
		    padding-right: 20px;
		}}

		.sum-part3 ul li .nobdrmail {{
		    border: none;
		}}

		.sum-part3 ul li img {{
		    width: 20px;
		}}

		.sum-btmpart {{
		    padding-top: 15px;
		}}

		.sum-btmpart p {{
		    font-size: 24px;
		    font-weight: bold;
		}}

		.sum-btmp2 {{    
		    border: 1px solid #3F4748;
		}}

		.sum-btmp3 {{    
		    border-bottom: 1px solid #3F4748;   
		}}

		.sumbdr {{
		    border-left: 1px solid #3F4748;
		}}

		.sumbtn-ctn p {{
		    padding: 20px;
		    font-size: 20px;
		    line-height: 32px;
		    font-style: italic;
		    margin: 0;
		}}

		.subbtn-right {{    
		   text-align: center;
		}}

		.subbtn-right img {{
		    width: 100px;  
		    margin-top: 40px;
		}}

		.sumbtnp4 p {{
		    font-size: 24px;
		    padding: 10px 20px;
		    margin: 0;
		}}

		.extrabdr {{
		    border-bottom: 1px solid #3F4748;
		    padding: 10px 0 10px;
		    margin-bottom: 5px;
		}}



		/*fsocial-area start*/
		.fsocial-area {{
		    padding: 0px 0 20px;
		}}

		.fscl-part img {{
		    width: 25px;
		    margin-right: 5px;
		    margin-bottom: 20px;
		}}



		/*
		====================================
		Medium Screen - Others
		====================================
		*/
		@media screen and (min-width: 992px) and (max-width: 1200px) {{


		}}

		/*
		====================================
		Small Screen - Tablate
		====================================
		*/
		@media screen and (min-width: 768px) and (max-width: 991px) {{

		.copy-left p {{
		    font-size: 15px;
		}}

		.copy-right p {{
		    font-size: 15px;
		}}

		.logo-left a img {{
		    width: 200px;
		}}

		.logrp1 h6 {{
		    font-size: 20px;
		}}

		.logrp2 h6 {{
		    font-size: 18px;   
		}}

		.logrp3 h4 {{
		    font-size: 25px;
		    text-align: right;  
		}}

		.sum-part1 h6 {{
		    font-size: 18px;
		}}

		.sum-part1 h6 .sum-ctn {{    
		    font-size: 30px;
		}}

		.sum-part1 .sumpt1 {{
		    font-size: 18px;
		}}

		.sum-part1 .sumpt2 {{
		    font-size: 18px;
		}}

		.sum-part1 p {{
		    font-size: 20px;    
		}}

		.sum-part2 ul li {{
			 font-size: 18px;
		    border-right: 1px solid #3F4748;
		    margin-right: 5px;    
		    padding-right: 20px;    
		}}

		.sum-part3 ul li {{
		    font-size: 18px;
		}}

		.sum-btmpart p {{
		    font-size: 18px;
		}}

		.sumbtn-ctn p {{
		    padding: 15px;
		    font-size: 16px;
		    line-height: 26px;
		}}



		.logo-right:after {{    
		    height: 85px;
		    right: 0;
		    bottom: -24px;
		    

		}}


		.logrgtp:after {{    
		    height: 35px;
		    bottom: -12px;
		      
		}}












		}}



		/*
		====================================
		Small Screen - Mobile
		====================================
		*/
		@media screen and (max-width: 767px) {{

		.copyright-area {{
		    padding: 25px 0 0px;
		}}

		.copy-left p {{
		    font-size: 16px;
		    text-align: center;
		    padding-bottom: 10px;
		}}

		.copy-right p {{
		    font-size: 16px;
		    text-align: center;
		}}

		.logo-area {{
		    padding: 10px 0 20px;
		}}

		.logo-left {{
			/*! padding-bottom: 24px; */
			padding: 15px 0;
		}}

		.logo-left a img {{
		    width: 200px;
		}}

		.logrp1 h6 {{
		    font-size: 20px;
		}}

		.logrp2 h6 {{
		    font-size: 18px;
		    text-align: center;  
		}}

		.logrp3 h4 {{
		    font-size: 25px;
		    text-align: center;
		    padding: 15px 0px
		}}

		.summer-area {{
		    padding: 10px 0 20px;
		}}

		.sum-part1 h6 {{
		    font-size: 16px;
		}}

		.sum-part1 h6 .sum-ctn {{    
		    font-size: 25px;
		}}

		.sum-part1 .sumpt1 {{
		    font-size: 16px;
		}}

		.sum-part1 .sumpt2 {{
		    font-size: 16px;
		}}

		.sum-part1 p {{
		    font-size: 18px;    
		}}

		.sum-part2 ul {{    
		    padding-bottom: 5px;
		}}

		.sum-part2 ul li {{
			 font-size: 16px;
		    border-right: none;
		    margin-right: 5px;    
		    padding-right: 20px;    
		}}

		.sum-part3 ul li {{
		    font-size: 16px;
		}}

		.sum-btmpart p {{
		    font-size: 16px;
		}}

		.sumbtn-ctn p {{
		    padding: 10px 15px;
		    font-size: 16px;
		    line-height: 26px;
		}}

		.sumbdr {{
		    border-top: 1px solid #3F4748;
		    border-left: none;
		    margin: 15px;
		}}

		.subbtn-right img {{     
		    margin-top: 20px;
		}}

		.copybdr {{
		    border-right: none;
		}}

		.logobdr {{
		    border-right: none;
		}}


		.sum-part1 .sumbdr2 {{
		    border-left: none;
		    border-right: none;
		    padding: 0 10px;
		}}

		.sum-part1 h6 {{     
		    padding-bottom: 10px;
		    line-height: 28px;
		}}

		.sum-part3 ul li:last-child span {{
			border: none;
		}}




		.logo-right:after {{    
		    display: none;
		    

		}}


		.logrgtp:after {{    
		    height: 35px;
		    bottom: -12px;
		      
		}}

		}}



		.row {{
			display: -webkit-box; /* wkhtmltopdf uses this one */
			display: flex;
			-webkit-box-pack: center; /* wkhtmltopdf uses this one */
			justify-content: center;
		}}

		.row > div {{
			-webkit-box-flex: 1;
			-webkit-flex: 1;
			flex: 1;
		}}

		.row > div:last-child {{
			margin-right: 0;
		}}

	</style>	


		
	</head>
	<body>
		<!--[if lte IE 9]>
            <p class="browserupgrade">You are using an <strong>outdated</strong> browser. Please <a href="https://browsehappy.com/">upgrade your browser</a> to improve your experience and security.</p>
        <![endif]-->


        <div class="full-area">
        	
		<!-- copyright-area start -->	
		<div class="copyright-area">
			<div class="container">
				<div class="copy-wrap">
					<div class="row align-items-center">
						<div class="col-md-8 copybdr">
							<div class="copy-left">
								<p style="font-size: 16px">Copyright © 2016 Production Telegram. All rights reserved</p>
							</div>
						</div>
						<div class="col-md-4">
							<div class="copy-right">
								<p>Issue No. {issue_num} </p>
							</div>
						</div>							
					</div>					
				</div>
			</div>
		</div>	
		<!-- copyright-area end -->

		<!-- logo-area start -->
		<div class="logo-area">
			<div class="container">
				<div class="logo-wrap">
					<div class="row no-gutters align-items-center">
						<div class="col-lg-7 col-md-6 logobdr">
							<div class="logo-left">
								<a href="#"><img src="https://i.ibb.co/k1SFpP6/logo.png" alt="logo" class="img-fluid"></a>
							</div>
						</div>
						<div class="col-lg-5 col-md-6">
							<div class="logo-right">
								<div class="logrgt">
									<div class="row no-gutters align-items-center">
										<div class="col-6">
											<div class="logrp1 ">
												<h6> {letter_creation_date} </h6>
											</div>
										</div>
										<div class="col-6 ">
											<div class="logrp2 logrgtp">
												<h6>Batch No. {batch_no} </h6>
											</div>
										</div>
									</div>
								</div>
								
								<div class="logrp3">
									<h4>WEEKLY TELEGRAM</h4>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		<!-- logo-area end -->

		<!-- summer-area start -->
		<div class="summer-area">
			<div class="container">

				<div class="summer-wrapper">
					<div class="sum-part1">
						<h6><span class="sum-ctn"> {title} </span> <span class="sumbdr2"> {project_start_date} </span> | {project_type} </h6>
						<ul>
							<li class="sumpt1">Listing</li>
							<li class="sumpt2">No {listing} </li>
						</ul>
						<p><img src="https://i.ibb.co/qY0RF7S/mail.png" alt="mail"/>pre production</p>
						<p class="sumbulctn"> {production_companies} <span class="sumplus">+</span> </p>
					</div>

					<div class="sum-part2">
						<ul>
							<li><strong>CONTACT:</strong>  </li>
						</ul>
					</div>

					<div class="sum-part3">
						<ul>
							<li>
								<span><strong>START DATE:</strong> {project_issue_date1} </span>
							</li>
							<li><span><strong>LOCATION:</strong> {locations} </span></li>
							<li><span><strong>DIRECTOR:</strong> {directors} </span></li>
							<li><span><strong>PRODUCER:</strong> {producers} </span></li>
							<li><span><strong>WRITER:</strong> {writers} </span></li>
							
						
						</ul>
					</div>

					<div class="sum-btmpart">
						<p style="font-size: 16px">({project_issue_date} - {release_date})</p>
						<div class="sum-btmp2">
							<div class="sum-btmp3">
								<div class="row">
									<div class="col-9">
										<div class="sumbtn-ctn">
											<p> {plot} </p>
										</div>
									</div>
									<div class="col-3 sumbdr">
										<div class="subbtn-right">
											<img src="https://i.ibb.co/JFkqLtb/tvimg.png" alt="tvimg">
										</div>
									</div>
								</div>
								
							</div>
							<div class="sumbtnp4">
									<p>/   .. //    -</p>
								</div>
						</div>
					</div>
					<div class="extrabdr">
						
					</div>
				</div>
			</div>
		</div>
		<!-- summer-area end -->
	

		<!-- fsocial-area start -->
		<div class="fsocial-area">
			<div class="container">
				<div class="fscl-part">
					<a href="#"><img src="https://i.ibb.co/qY0RF7S/mail.png" alt="mail"/></a>
					<a href="#"><img src="https://i.ibb.co/qY0RF7S/mail.png" alt="mail"/></a>
					<a href="#"><img src="https://i.ibb.co/qY0RF7S/mail.png" alt="mail"/></a>
					
				</div>
			</div>
		</div>
		<!-- fsocial-area end -->

		</div>

		<!-- Fontawesome Script -->
		<script src="https://kit.fontawesome.com/7749c9f08a.js"></script>	
		
		<!-- Scroll-Top button -->
		<a href="#" class="scrolltotop"><i class="fas fa-angle-up"></i></a>
		
	</body>
</html>
'''