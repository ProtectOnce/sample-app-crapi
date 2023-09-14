from locust import HttpUser, between, task 
import random

new_ctr = 1
with open("users.txt") as file_in:
    users = []
    for line in file_in:
        users.append(line.replace("\n",""))

class WebsiteUser(HttpUser):
    wait_time = between(1,3)
    tokens = set()
    boolean_rand = [True,False]
    ctr = 1

    endpoints = [
        ".well-known/jwks.json","identity/api/v2/user/dashboard","workshop/api/shop/products",
        "community/api/v2/community/posts/recent","rest/order-history","api/Recycles/","identity/api/v2/vehicle/vehicles"
    ]

    def on_start(self):
        global new_ctr
        global users
        login =  "identity/api/auth/login"
        creds = {"email": random.choice(users), "password": "Test@123"}
        res = self.client.post(login, json=creds).json()
        new_ctr = new_ctr + 1
        self.tokens.add(res["token"])
        self.applyCoupon(res["token"])

    def applyCoupon(self,token):
        verify = {"coupon_code": "TRAC075"}
        headers = {"Authorization":"Bearer " + token}
        self.client.post("community/api/v2/coupon/validate-coupon", headers=headers, json=verify)
        coupon = {"amount": 50000, "coupon_code": "TRAC075"}
        self.client.post("workshop/api/shop/apply_coupon", headers=headers, json=coupon)

    @task(2)
    def getLocation(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        vehicle = self.client.get("identity/api/v2/vehicle/vehicles",headers=headers).json()
        vid = vehicle[0]["uuid"]
        vehicle = self.client.get("identity/api/v2/vehicle/"+ vid + "/location",headers=headers).json()

    @task
    def makeRestCall(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        self.client.get(random.choice(self.endpoints),headers=headers)

    @task
    def getReport(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        randint = random.randint(1,5)
        self.client.get("workshop/api/mechanic/mechanic_report?report_id="+str(randint),headers=headers)

    @task
    def contactMechanic(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        res = self.client.get("identity/api/v2/vehicle/vehicles",headers=headers).json()
        contact={
            "mechanic_api": "http://127.0.0.1:8888/workshop/api/mechanic/receive_report",
            "mechanic_code": "TRAC_JHN", "number_of_repeats": 1, "problem_details": "Test message",
            "repeat_request_if_failed": False, "vin": res[0]["vin"]
        }
    
    @task
    def verifyToken(self):
        random_token = random.sample(self.tokens,1)[0]
        self.client.post("identity/api/auth/verify", json={"token": random_token})

    @task
    def createPost(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        post = {"title":"Test post ","content":"randomLoremParagraph"}
        self.client.post("community/api/v2/community/posts", json=post,headers=headers)

    @task
    def getPost(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        res = self.client.get("community/api/v2/community/posts/recent", headers=headers).json()
        pid = random.choice(res)["id"]
        self.client.get("community/api/v2/community/posts/"+pid, headers=headers).json()
        comment={"content": "Test"}
        self.client.post("community/api/v2/community/posts/" + pid + "/comment", headers=headers, json=comment)

    @task(2)
    def makePurchase(self):
        random_token = random.sample(self.tokens,1)[0]
        headers = {"Authorization":"Bearer " + random_token}
        purchase = {"product_id": 1, "quantity": 1}
        res = self.client.post("workshop/api/shop/orders", headers=headers, json=purchase).json()
        self.client.get("workshop/api/shop/orders/" + str(res["id"]), headers=headers)
        if random.choice(self.boolean_rand):
            self.client.post("workshop/api/shop/orders/return_order?order_id="+ str(res["id"]), headers=headers)
            data = {
                "product_id": 1,
                "quantity": 1,
            }
            res = self.client.get("workshop/api/shop/orders/all", headers=headers).json()
            orders = res["orders"]
            self.client.put("workshop/api/shop/orders/"+str(random.choice(orders)["id"]), json=data,headers=headers)