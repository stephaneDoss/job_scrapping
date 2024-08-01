from flask import Flask, request, jsonify
from scrapping import search_jobs, scrape_job_details, clean_data, export_to_csv
from model import Job

app = Flask(__name__)


@app.route('/scrape_jobs', methods=['GET'])
def scrape_jobs_api():
    job_title = request.args.get('job_title')

    if not job_title:
        return jsonify({'error': 'Veuillez fournir un titre d\'emploi'}), 400

    driver = search_jobs(job_title)
    job_data = scrape_job_details(driver)
    cleaned_job_data = clean_data(job_data)
    driver.quit()

    jobs = []
    for entry in cleaned_job_data:
        job = Job(**entry)
        jobs.append(job.__dict__)

    return jsonify({'jobs': jobs}), 200


if __name__ == '__main__':
    app.run(debug=True)
