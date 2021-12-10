

            
        return True

    # Related To Finding Filter(s)
    async def add_filters(self, data):
        """
        A Funtion to add document as
        a bulk to db
        """
        try:
            await self.fcol.insert_many(data)
        except Exception as e:
            print(e)
        
        return True


    async def del_filters(self, group_id: int, channel_id: int):
        """
        A Funtion to delete all filters of a specific
        chat and group from db
        """
        group_id, channel_id = int(group_id), int(channel_id)
        
        try:
            await self.fcol.delete_many({"chat_id": channel_id, "group_id": group_id})
            print(await self.cf_count(group_id, channel_id))
            return True
        except Exception as e:
            print(e) 
            return False


    async def delall_filters(self, group_id: int):
        """
        A Funtion To delete all filters of a group
        """
        await self.fcol.delete_many({"group_id": int(group_id)})
        return True


    async def get_filters(self, group_id: int, keyword: str):
        """
        A Funtion to fetch all similar results for a keyowrd
        from using text index
        """
        await self.create_index()

        chat = await self.find_chat(group_id)
        chat_accuracy = float(chat["configs"].get("accuracy", 0.80))
        achats = await self.find_active(group_id)
        
        achat_ids=[]
        if not achats:
            return False
        
        for chats in achats["chats"]:
            achat_ids.append(chats.get("chat_id"))
        
        filters = []
                
        pipeline= {
            'group_id': int(group_id), '$text':{'$search': keyword}
        }
        
        
        db_list = self.fcol.find(
            pipeline, 
            {'score': {'$meta':'textScore'}} # Makes A New Filed With Match Score In Each Document
        )

        db_list.sort([("score", {'$meta': 'textScore'})]) # Sort all document on the basics of the score field
        
        for document in await db_list.to_list(length=600):
            if document["score"] < chat_accuracy:
                continue
            
            if document["chat_id"] in achat_ids:
                filters.append(document)
            else:
                continue

        return filters


    async def get_file(self, unique_id: str):
        """
        A Funtion to get a specific files using its
        unique id
        """
        file = await self.fcol.find_one({"unique_id": unique_id})
        file_id = None
        file_type = None
        file_name = None
        file_caption = None
        
        if file:
            file_id = file.get("file_id")
            file_name = file.get("file_name")
            file_type = file.get("file_type")
            file_caption = file.get("file_caption")
        return file_id, file_name, file_caption, file_type


    async def cf_count(self, group_id: int, channel_id: int):
        """
        A Funtion To count number of filter in channel
        w.r.t the connect group
        """
        return await self.fcol.count_documents({"chat_id": channel_id, "group_id": group_id})
    
    
    async def tf_count(self, group_id: int):
        """
        A Funtion to count total filters of a group
        """
        return await self.fcol.count_documents({"group_id": group_id})


