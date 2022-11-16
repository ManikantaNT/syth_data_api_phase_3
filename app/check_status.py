# importing the libraries
from smtplib import SMTP
from redmail import EmailSender


def simple_send(email_ids, epochs, size, gen_dim, log_freq, emb_dim, dis_dim, b_size, id, status,
                starting_time, ending_time, quality_score_overall, quality_score_column_wise,
                quality_score_pairwise,path):
	em = EmailSender(username="tarun81998@gmail.com",
	                 password="vwhybyhsqmmxkhrs",
	                 host="smtp.gmail.com",
	                 port=587,
	                 cls_smtp=SMTP,
	                 use_starttls=True
	                 )
	em.send(
		subject="An email",
		sender="tarun81998@gmail.com",
		receivers=email_ids,
		text="Hi, this is an email regarding your synthetic data generation.",
		html=f'''<HTML>
				<h1> Data is generated </h1>
		        <h3>Metadata about generation</h3>
		        <table style="width: 100%;" border="2" cellspacing="2" cellpadding="2" bgcolor="lightblue">				
				<tr>
				<th>Epochs</th>
				<th>Synthetic Data Size</th>
				<th>generator_dim</th>	
				<th>log_frequency</th>				
				<th>embedding_dim</th>				
				<th>discriminator_dim</th>				
				<th>Batch Size</th>				
				</tr>	        
		        <tr>
		        <td>{epochs}</td>
		        <td>{size}</td>
		        <td>{gen_dim}</td>
		        <td>{log_freq}</td>
		        <td>{emb_dim}</td>
		        <td>{dis_dim}</td>
		        <td>{b_size}</td>
		        </tr>
		        </table>
				
				<br>
				<br>
		        
		        <h3>Task Report</h3>
		        <table style="width: 100%;" border="2" cellspacing="2" cellpadding="2" bgcolor="lightgreen">
				<tr>
				<th>TaskID</th>
				<th>Status</th>
				<th>Path</th>
				<th>Starting Time</th>
				<th>Ending Time</th>
				</tr>
		        <tr>
		        <td>{id}</td>
		        <td>{status}</td>
		        <td>{path}</td>
		        <td>{starting_time}</td>
		        <td>{ending_time}</td>
		        </tr>
		        </table>

				<br>
				<br>

		        <h3>Quality Report</h3> 
		        <table style = "width: 100%;"border="2" cellspacing="2" cellpadding="2" bgcolor="#ffff00">
				<tr>
				<th>Quality Score Overall</th>
				<th>Quality Score Column Wise</th>
				<th>Quality Score Pairwise</th>
				</tr>
		        <tr>
		        <td>{quality_score_overall}</td>
		        <td>{quality_score_column_wise}</td>
		        <td>{quality_score_pairwise}</td>
		        </tr>   
		        </table>

		        <HTML>'''
	)
