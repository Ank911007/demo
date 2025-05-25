from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os, subprocess, uuid, shutil

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"

@app.route("/deploy", methods=["POST"])
def deploy():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    unique_id = str(uuid.uuid4())
    temp_dir = os.path.join(UPLOAD_FOLDER, unique_id)
    os.makedirs(temp_dir)

    try:
        template_file = request.files["template"]
        provider = request.form["provider"]
        access_key = request.form["access_key"]
        secret_key = request.form["secret_key"]

        zip_path = os.path.join(temp_dir, secure_filename(template_file.filename))
        template_file.save(zip_path)

        subprocess.run(["unzip", zip_path, "-d", temp_dir], check=True)
        terraform_dir = temp_dir

        # Set environment variables for cloud credentials
        env = os.environ.copy()
        if provider == "aws":
            env["AWS_ACCESS_KEY_ID"] = access_key
            env["AWS_SECRET_ACCESS_KEY"] = secret_key
        elif provider == "azure":
            env["ARM_CLIENT_ID"] = access_key
            env["ARM_CLIENT_SECRET"] = secret_key
        else:
            return jsonify({"status": "error", "message": "Invalid cloud provider"}), 400

        # Run Terraform init
        init = subprocess.run(["terraform", "init"], cwd=terraform_dir, capture_output=True, text=True, env=env)
        init_log = init.stdout + init.stderr

        # Run Terraform apply
        apply = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir, capture_output=True, text=True, env=env)
        apply_log = apply.stdout + apply.stderr

        # Get Terraform output
        output = subprocess.run(["terraform", "output", "-json"], cwd=terraform_dir, capture_output=True, text=True, env=env)

        return jsonify({
            "status": "success",
            "init_log": init_log,
            "apply_log": apply_log,
            "outputs": output.stdout
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500
    finally:
        shutil.rmtree(temp_dir)

@app.route("/")
def index():
    return render_template("index.html")  # Serve the frontend form

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

