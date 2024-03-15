import gradio as gr
from requests.exceptions import ConnectTimeout
import time
import requests
import base64

global headers
global cancel_url
global path
global output_image
global property_name_array
property_name_array =[]
output_image = ''
path = ''
cancel_url =''
headers = {   
        'Content-Type': 'application/json',
        'Authorization': 'Token r8_ZGZlzThfRkPZVDMygVclY1XZ9AuxmIQ2qwwPP',
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": '**',
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PATCH"}

with gr.Blocks() as demo:
    owner = "lucataco"
    name = "moondream1"
    max_retries = 3
    retry_delay = 2
    for retry in range(max_retries):
       try:
          url = f'https://api.replicate.com/v1/models/{owner}/{name}'
          response = requests.get(url,  headers=headers, timeout=10)
        # Process the response
          break  # Break out of the loop if the request is successful
       except ConnectTimeout:
        if retry < max_retries - 1:
            print(f"Connection timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Max retries exceeded. Unable to establish connection.")

    data = response.json()
    description =data.get("description", '')
    title = data.get("default_example",'').get("model",'')
    version = data.get("default_example",'').get("version",'')

    gr.Markdown(
    f"""
    # {title}
     {description}
    """)

    with gr.Row():
        with gr.Column():
            inputs =[]
            schema = data.get("latest_version", {}).get("openapi_schema", {}).get("components", {}).get("schemas", {})
            ordered_properties = sorted(schema.get("Input", {}).get("properties", {}).items(), key=lambda x: x[1].get("x-order", 0))
            required = schema.get("Input", '').get('required', [])
            print(required,"required")
            for property_name, property_info in ordered_properties :
                property_name_array.append(property_name)
                if required:
                    for item in required:
                        if item ==  property_name:
                            label = "*"+ property_info.get('title', '')
                            description = property_info.get('description','')
                            break
                        else:
                            label = property_info.get('title', '')
                            description = property_info.get('description','')
                else:
                     label = property_info.get('title', '')
                     description = property_info.get('description','')

                if "x-order" in property_info:
                    order = int(property_info.get('x-order',''))
                    if property_info.get("type", {}) == "integer":
                        value= data.get('default_example', '').get('input','').get(property_name,0)
                        if "minimum" and "maximum" in property_info:
                            if value == 0:
                              inputs.insert(order, gr.Slider(label=label, info= description, value=property_info.get('default', value), minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', ''), step=1))
                            else:
                              inputs.insert(order, gr.Slider(label=label, info= description, value=value, minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', ''), step=1)) 
                        else:
                            if value == 0:
                               inputs.insert(order, gr.Number(label=label, info= description, value=property_info.get('default', value)))
                            else:
                               inputs.insert(order, gr.Number(label=label, info= description, value=value))
                            
                    elif property_info.get("type", {}) == "string":
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        if  property_info.get('format','') == 'uri':
                          
                                if value :
                                        inputs.insert(order, gr.Image(label=label, value=value, type="filepath"))
                                else :
                                        inputs.insert(order, gr.Image(label=label, type="filepath"))
                          
                        else:
                            if value == '':
                               inputs.insert(order, gr.Textbox(label=label,info= description, value=property_info.get('default', value)))
                            else:
                               inputs.insert(order, gr.Textbox(label=label,info= description, value=value))

                    elif property_info.get("type", {}) == "number":
                        value= data.get('default_example', '').get('input','').get(property_name, 0)
                        if "minimum" and "maximum" in property_info:
                            if value == 0:
                                inputs.insert(order, gr.Slider(label=label,info= description, value=property_info.get('default', value), minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', '')))
                            else:
                                inputs.insert(order, gr.Slider(label=label,info= description, value=value, minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', '')))
                        else:
                            if value == 0:
                              inputs.insert(order, gr.Number(label=label,info= description, value=property_info.get('default', value)))
                            else:
                              inputs.insert(order, gr.Number(label=label,info= description, value=value)) 
                    elif property_info.get("type", {}) == "boolean":
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        if value == '':
                           inputs.insert(order, gr.Checkbox(label=label,info= description, value=property_info.get('default', value)))
                        else:
                            inputs.insert(order, gr.Checkbox(label=label,info= description, value=value))
                    else :
                         value= data.get('default_example', '').get('input','').get(property_name,'')
                         if value == '':
                           inputs.insert(order, gr.Textbox(label=label,info= description, value=property_info.get('default', value)))
                         else:
                            inputs.insert(order, gr.Textbox(label=label,info= description, value=value))
                  
             
            with gr.Row():
                cancel_btn = gr.Button("Cancel")
                run_btn = gr.Button("Run")
                 
        with gr.Column():
            
            outputs = []

            output_result = data.get("default_example", '').get("output")
            output_type= schema.get("Output", '').get("type", '')
            if output_type == 'array':
                    output_image =  ''.join(output_result)
            else:
                output_image = output_result
            print (output_image)
            outputs.append(gr.TextArea(value=output_image))
            outputs.append(gr.Image(visible=False))
            outputs.append(gr.Image(visible=False))
            outputs.append(gr.Image(visible=False))
            
           
    
    def run_process(input1, input2):
       global cancel_url
       global property_name_array
       print(len(property_name_array))
       cancel_url=''
       url = 'https://replicate.com/api/predictions'
      
       if input1:
            with open(input1, "rb") as file:
                data = file.read()

            base64_data = base64.b64encode(data).decode("utf-8")
            mimetype = "image/jpg"
            data_uri_image = f"data:{mimetype};base64,{base64_data}"
       else:
           data_uri_image=None

       print(version, 'version')
       if input1:
            body = {
                    "version": version,
                    "input": {
                            property_name_array[0]: data_uri_image,
                            property_name_array[1]: input2,

                    }
                    }
     
       else:
             body = {
                    "version": version,
                    "input": {
                            property_name_array[1]: input2,
  
                    }
                    }
         
    
       response = requests.post(url, json=body)
       print(response.status_code)
       if response.status_code == 201:
            response_data = response.json()
            get_url = response_data.get('urls','').get('get','')
            identifier = 'https://replicate.com/api/predictions/'+get_url.split("/")[-1]
            
            print(identifier,'')
            time.sleep(3)
            output =verify_image(identifier) 
            print(output,'333')
            if output:
                     return  gr.TextArea(value=''.join(output)), gr.Image(),gr.Image(),gr.Image()
                
       return gr.Image(),gr.Image(visible=False),gr.Image(visible=False),gr.Image(visible=False)
    
    def cancel_process(input1, input2):
        global cancel_url
        cancel_url = '123'
        global output_image
        return gr.TextArea(value=output_image), gr.Image(visible=False),gr.Image(visible=False),gr.Image(visible=False)

    def verify_image(get_url):
        res = requests.get(get_url)
        if res.status_code == 200:
            res_data = res.json()
            if res_data.get('error',''):
                return
            else:
               if cancel_url:
                   return
               else:
                    output =  res_data.get('output', [])
                    print(output,'111')
                    if output:
                        print(output,'222')
                        return output
                        
                    else:
                        time.sleep(1)
                        val = verify_image(get_url)
                        return val
        else: 
            return  []  
    
    run_btn.click(run_process, inputs=inputs, outputs=outputs, api_name="run")
    cancel_btn.click(cancel_process, inputs=inputs, outputs=outputs, api_name="cancel")

demo.launch()


         


