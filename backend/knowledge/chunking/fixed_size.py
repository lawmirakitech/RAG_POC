from typing import Optional, Any, Dict, List
import asyncio
class FixedChunking:

    def __init__(self):
        self.chunk_size = 1000
        self.overlap = 100

    async def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Chunk text into fixed-size pieces."""
        if metadata is None:
            metadata = {}
            
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            if chunk_text.strip():
                # chunk_metadata = self._create_chunk_metadata(
                #     chunk_index=chunk_index,
                #     start_pos=start,
                #     end_pos=end,
                #     text=chunk_text,
                #     metadata=metadata
                # )
                
                chunks.append(chunk_text)
                chunk_index += 1
            
            start += self.chunk_size - self.overlap
        
        return chunks
    


if __name__ == "__main__":

    fc = FixedChunking()
    print()
    text = asyncio.run(fc.chunk("Artificial intelligence is fundamentally reshaping the future of human society in countless ways that span across every major industry and aspect of daily life It represents a paradigm shift comparable to the industrial revolution or the dawn of the internet fundamentally altering how we work live and interact with the world at large The power of AI lies in its ability to process vast quantities of data identify intricate patterns and learn from experience at a scale and speed far beyond human capability This capacity is driving innovation and efficiency but also raising profound ethical social and economic questions that will define the coming decades At its core AI encompasses a wide range of technologies including machine learning deep learning and natural language processing which together enable machines to simulate human-like intelligence These technologies are not merely augmenting existing processes they are creating entirely new ones and opening up possibilities that were once confined to the realm of science fiction \
                             In healthcare AI is revolutionizing how diseases are diagnosed and treated AI algorithms can analyze medical imagery such as x rays and MRIs with incredible precision often detecting subtle anomalies that might be missed by human eyes This allows for earlier and more accurate diagnosis of conditions like cancer and neurological disorders Furthermore AI is at the forefront of personalized medicine analyzing a patient s genetic data medical history and lifestyle factors to develop highly customized treatment plans that maximize effectiveness and minimize side effects AI powered drug discovery platforms are accelerating the process of developing new medicines by simulating the effects of different compounds dramatically reducing the time and cost associated with traditional research In surgical settings AI assisted robotic systems provide surgeons with enhanced precision and control enabling less invasive procedures with faster recovery times The future of healthcare promises a deeper integration of AI from predictive analytics that forecast disease outbreaks to AI driven virtual assistants that help patients manage their health The business and finance sectors are being transformed by AI driven automation and enhanced decision making AI is being used to automate repetitive and manual tasks through robotic process automation freeing human workers to focus on more complex and creative endeavors In finance AI plays a critical role in fraud detection by monitoring millions of transactions in real time and flagging suspicious activities with a high degree of accuracy AI algorithms are also used for high frequency trading and market analysis providing insights that inform investment strategies For customer service AI powered chatbots and virtual assistants provide instant support improving customer satisfaction and operational efficiency In retail AI driven recommendation engines analyze consumer behavior to provide personalized product suggestions driving sales and enhancing the shopping experience Supply chain logistics are being optimized by AI which can predict demand manage inventory and plan the most efficient delivery routes The result is a more agile and responsive business landscapeThe transportation industry is undergoing a massive change driven by AI most notably in the development of autonomous vehicles Self driving cars trucks and drones use AI combined with sensors and computer vision to navigate complex environments promising safer more efficient and more accessible travel AI traffic management systems are being deployed in smart cities to reduce congestion optimize traffic flow and lower emissions The future will likely see a vast network of interconnected autonomous vehicles and a redefinition of personal and public transportation Education is another area where AI is poised to make a significant impact AI powered adaptive learning platforms can tailor educational content and assessments to each student s individual pace learning style and abilities providing a highly personalized educational experience Intelligent tutoring systems can provide students with one on one guidance and support reinforcing concepts and helping them overcome challenges AI can also automate administrative tasks for educators such as grading and scheduling allowing teachers to dedicate more time to mentorship and one on one student interaction This has the potential to make high quality personalized education more accessible to a broader population helping to bridge existing educational disparities The rise of AI also brings with it a host of significant ethical and societal challenges one of the most pressing being job displacement and the future of work As AI automates more routine tasks many jobs particularly in manufacturing transportation and administrative roles could be at risk of automation While AI will undoubtedly create new jobs the nature of work will change requiring a massive investment in workforce retraining and upskilling to prevent widespread unemployment and widening socioeconomic disparities Another major concern is algorithmic bias AI systems are only as unbiased as the data they are trained on If the training data reflects existing human biases the AI will amplify and perpetuate them leading to discriminatory outcomes in areas like hiring lending and criminal justice Addressing this requires diverse data sets and transparent development processes Data privacy and surveillance are also critical issues as AI relies on vast amounts of personal data to function Striking a balance between the benefits of data driven innovation and the need to protect individual privacy is a difficult challenge that will necessitate strong data protection regulations and transparent practices Furthermore the black box nature of some advanced AI algorithms makes it difficult to understand how they arrive at their decisions This lack of transparency can erode trust and complicate accountability particularly in high stakes applications like medical diagnosis or legal proceedings The emerging field of explainable AI or XAI is focused on developing methods to make these systems more understandable and transparent"))
    for t in text:
        print(len(t))